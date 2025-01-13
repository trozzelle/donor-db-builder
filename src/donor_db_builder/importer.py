# import hashlib
# import re
# import tempfile
# import uuid
# from pathlib import Path
#
# import numpy as np
# import pandas as pd
# from gqlalchemy import Memgraph, create, merge
# from loguru import logger
# from neo4j import GraphDatabase
#
# from models.Contribution import Contribution, Made, To
# from models.Donor import Donor
# from models.Filer import Filer
# from src.donor_db_builder.utils.logger import Logger
#
# logger = Logger.get_logger()
#
#
# class DonorGraph:
#     """Class for experimenting with different methods of importing data into memgraph"""
#
#     def __init__(self, host: str, port: int, username: str, password: str):
#         # self.db = GraphDatabase.driver(uri, auth=(username, password))
#         self.db = Memgraph(host=host, port=port, username=username, password=password)
#         logger.info("Initializing DonorGraph")
#
#     def setDriver(self, uri: str, username: str, password: str):
#         self.driver = GraphDatabase.driver(uri, auth=(username, password))
#
#     def close(self):
#         logger.info("Closing DB connection")
#         self.db.close()
#
#     @logger.catch
#     def clear_database(self):
#         logger.debug("Deleting all nodes and relationships")
#         self.db.execute("MATCH (n) DETACH DELETE n")
#         logger.info("Database cleared successfully")
#
#     def generate_donor_id(self, row: pd.Series) -> str:
#         """Generate unique ID for donor by hashing their attributes"""
#         if pd.isna(row["FLNG_ENT_FIRST_NAME"]):
#             key_parts = [
#                 str(row["FLNG_ENT_NAME"]).upper(),
#                 str(row["FLNG_ENT_ADD1"]).upper(),
#                 str(row["FLNG_ENT_ZIP"])[:5],
#             ]
#         else:
#             key_parts = [
#                 str(row["FLNG_ENT_FIRST_NAME"]).upper(),
#                 str(row["FLNG_ENT_LAST_NAME"]).upper(),
#                 str(row["FLNG_ENT_ADD1"]).upper(),
#                 str(row["FLNG_ENT_ZIP"])[:5],
#             ]
#
#         key = "|".join(filter(None, key_parts))
#         return hashlib.md5(key.encode()).hexdigest()
#
#     def clean_name(self, name: str) -> str:
#         if pd.isna(name):
#             return ""
#
#         name = re.sub(r"\s+(Inc\.?|LLC|Corp\.?|LLP)$", "", name, flags=re.IGNORECASE)
#
#         return name.strip()
#
#     @logger.catch
#     def import_data(self, contributions_df: pd.DataFrame, filers_df: pd.DataFrame):
#         logger.info("Starting data import")
#         logger.info(
#             "Processing {} filers and {} contributions",
#             len(filers_df),
#             len(contributions_df),
#         )
#
#         try:
#             with self.driver.session() as session:
#                 logger.info("Importing committees")
#
#                 ## Data cleanup
#                 # Split 'MUNICIPALITY_DESC, SUBDIVISION_DESC' column. This is concatenated into a single column in all
#                 # Socrata exports, not sure why
#                 filers_df[["MUNICIPALITY", "SUBDIVISION"]] = filers_df[
#                     "MUNICIPALITY_DESC, SUBDIVISION_DESC"
#                 ].str.split(",", expand=True)
#
#                 # Change NaN to None, interpreted as null by neo4j
#                 filers_df = filers_df.replace({np.nan: None})
#
#                 for i, row in filers_df.iterrows():
#                     try:
#                         session.run(
#                             """
#                                 MERGE (c:Committee {filer_id: $filer_id})
#                                 SET c.name = $name,
#                                     c.type = $type,
#                                     c.status = $status,
#                                     c.office = $office,
#                                     c.district = $district,
#                                     c.county = $county,
#                                     c.municipality = $municipality,
#                                     c.subdivision = $subdivision
#                             """,
#                             {
#                                 "filer_id": str(row["FILER_ID"]),
#                                 "name": row["FILER_NAME"],
#                                 "type": row["FILER_TYPE_DESC"],
#                                 "status": row["FILER_STATUS"],
#                                 "office": row["OFFICE_DESC"],
#                                 "district": row["DISTRICT"],
#                                 "county": row["COUNTY_DESC"],
#                                 "municipality": row["MUNICIPALITY"],
#                                 "subdivision": row["SUBDIVISION"],
#                             },
#                         )
#                         if (i + 1) % 100 == 0:
#                             logger.debug(f"Processed {i + 1} filers")
#                     except Exception as e:
#                         logger.error(
#                             "Error importing committee %s: %s", row["FILER_ID"], str(e)
#                         )
#                         raise
#
#                 logger.info("Importing donors and contributions")
#
#                 ## Data cleanup
#
#                 # Parse date strings into python datetime objects
#                 # contributions_df['SCHED_DATE'] = pd.to_datetime(contributions_df['SCHED_DATE'])
#                 # Change NaN to None, interpreted as null by neo4j
#                 contributions_df = contributions_df.replace({np.nan: None})
#
#                 for i, row in contributions_df.iterrows():
#                     try:
#                         donor_id = self.generate_donor_id(row)
#
#                         if pd.isna(row["FLNG_ENT_FIRST_NAME"]):
#                             donor_type = "Organization"
#                             donor_name = self.clean_name(row["FLNG_ENT_NAME"])
#                         else:
#                             donor_type = "Individual"
#                             donor_name = f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#
#                         session.run(
#                             """
#                                 MERGE (d:Donor {id: $donor_id})
#                                 SET d.name = $name,
#                                     d.type = $donor_type,
#                                     d.address = $address,
#                                     d.city = $city,
#                                     d.state = $state,
#                                     d.zip = $zip
#                             """,
#                             {
#                                 "donor_id": donor_id,
#                                 "name": donor_name,
#                                 "donor_type": donor_type,
#                                 "address": row["FLNG_ENT_ADD1"],
#                                 "city": row["FLNG_ENT_CITY"],
#                                 "state": row["FLNG_ENT_STATE"],
#                                 "zip": row["FLNG_ENT_ZIP"],
#                             },
#                         )
#
#                         # Create Contribution and relationships
#                         session.run(
#                             """
#                                 MATCH (d:Donor {id: $donor_id})
#                                 MATCH (c:Committee {filer_id: $filer_id})
#                                 CREATE (d)-[:MADE]->(t:Contribution {
#                                     amount: $amount,
#                                     date: localDateTime($date),
#                                     payment_type: $payment_type,
#                                     transaction_id: $transaction_id,
#                                     contributor_type: $contributor_type,
#                                     payment_method: $payment_method
#                                 })-[:TO]->(c)
#                             """,
#                             {
#                                 "donor_id": donor_id,
#                                 "filer_id": str(row["FILER_ID"]),
#                                 "amount": float(row["ORG_AMT"]),
#                                 "date": str(row["SCHED_DATE"]),
#                                 "payment_type": row["PAYMENT_TYPE_DESC"],
#                                 "transaction_id": row["TRANS_NUMBER"],
#                                 "contributor_type": row["CNTRBR_TYPE_DESC"],
#                                 "payment_method": row["PAYMENT_TYPE_DESC"],
#                             },
#                         )
#                         if (i + 1) % 100 == 0:
#                             logger.debug(f"Processed {i + 1} contributions")
#                     except Exception as e:
#                         logger.error(
#                             "Error importing contribution %s: %s",
#                             row["TRANS_NUMBER"],
#                             str(e),
#                         )
#                         raise
#
#                 logger.success("Data import completed successfully")
#
#         except Exception as e:
#             logger.error("Fatal error during data import: %s", str(e))
#             raise
#
#     @logger.catch
#     def import_data_from_model(
#         self, contributions_df: pd.DataFrame, filers_df: pd.DataFrame
#     ):
#         logger.info("Starting data import")
#         logger.info(
#             "Processing {} filers and {} contributions",
#             len(filers_df),
#             len(contributions_df),
#         )
#
#         try:
#             logger.info("Importing committees")
#
#             ## Data cleanup
#             # Split 'MUNICIPALITY_DESC, SUBDIVISION_DESC' column. This is concatenated into a single column in all
#             # Socrata exports, not sure why
#             filers_df[["MUNICIPALITY", "SUBDIVISION"]] = filers_df[
#                 "MUNICIPALITY_DESC, SUBDIVISION_DESC"
#             ].str.split(",", expand=True)
#
#             # Change NaN to None, interpreted as null by neo4j
#             filers_df = filers_df.replace({np.nan: None})
#
#             for i, row in filers_df.iterrows():
#                 try:
#                     filer = Filer(
#                         filer_id=str(row["FILER_ID"]),
#                         name=row["FILER_NAME"],
#                         type=row["FILER_TYPE_DESC"],
#                         status=row["FILER_STATUS"],
#                         office=row["OFFICE_DESC"],
#                         district=row["DISTRICT"],
#                         county=row["COUNTY_DESC"],
#                         municipality=row["MUNICIPALITY"],
#                         subdivision=row["SUBDIVISION"],
#                     ).save(self.db)
#                     if (i + 1) % 100 == 0:
#                         logger.debug(f"Processed {i+1} filers")
#                 except Exception as e:
#                     logger.error(
#                         "Error importing committee %s: %s", row["FILER_ID"], str(e)
#                     )
#                     raise
#
#             logger.info("Importing donors and contributions")
#
#             ## Data cleanup
#
#             # Parse date strings into python datetime objects
#             contributions_df["SCHED_DATE"] = pd.to_datetime(
#                 contributions_df["SCHED_DATE"]
#             )
#             # Change NaN to None, interpreted as null by neo4j
#             contributions_df = contributions_df.replace({np.nan: None})
#
#             for i, row in contributions_df.iterrows():
#                 try:
#                     donor_id = self.generate_donor_id(row)
#
#                     if pd.isna(row["FLNG_ENT_FIRST_NAME"]):
#                         donor_type = "Organization"
#                         donor_name = self.clean_name(row["FLNG_ENT_NAME"])
#                     else:
#                         donor_type = "Individual"
#                         donor_name = f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#
#                     # Create or merge donor
#                     donor = Donor(
#                         id=donor_id,
#                         name=donor_name,
#                         type=donor_type,
#                         address=row["FLNG_ENT_ADD1"],
#                         city=row["FLNG_ENT_CITY"],
#                         state=row["FLNG_ENT_STATE"],
#                         zip=row["FLNG_ENT_ZIP"],
#                     ).save(self.db)
#
#                     # Create contribution node
#                     contribution = Contribution(
#                         transaction_id=row["TRANS_NUMBER"],
#                         amount=float(row["ORG_AMT"]),
#                         date=row["SCHED_DATE"],
#                         payment_type=row["PAYMENT_TYPE_DESC"],
#                         contributor_type=row["CNTRBR_TYPE_DESC"],
#                         payment_method=row["PAYMENT_TYPE_DESC"],
#                     ).save(self.db)
#
#                     # Create relationships
#                     Made(_start_node_id=donor._id, _end_node_id=contribution._id).save(
#                         self.db
#                     )
#                     To(
#                         _start_node_id=contribution._id,
#                         _end_node_id=Filer(filer_id=str(row["FILER_ID"]))._id,
#                     ).save(self.db)
#
#                     if (i + 1) % 100 == 0:
#                         logger.debug(f"Processed {i + 1} contributions")
#                 except Exception as e:
#                     logger.error(
#                         "Error importing contribution %s: %s",
#                         row["TRANS_NUMBER"],
#                         str(e),
#                     )
#                     raise
#
#             logger.success("Data import completed successfully")
#
#         except Exception as e:
#             logger.error("Fatal error during data import: %s", str(e))
#             raise
#
#     @logger.catch
#     def import_data_from_query_builder(
#         self, contributions_df: pd.DataFrame, filers_df: pd.DataFrame
#     ):
#         logger.info("Starting data import")
#         logger.info(
#             "Processing {} filers and {} contributions",
#             len(filers_df),
#             len(contributions_df),
#         )
#
#         try:
#             logger.info("Importing committees")
#
#             ## Data cleanup
#             # Split 'MUNICIPALITY_DESC, SUBDIVISION_DESC' column. This is concatenated into a single column in all
#             # Socrata exports, not sure why
#             filers_df[["MUNICIPALITY", "SUBDIVISION"]] = filers_df[
#                 "MUNICIPALITY_DESC, SUBDIVISION_DESC"
#             ].str.split(",", expand=True)
#
#             # Change NaN to None, interpreted as null by neo4j
#             filers_df = filers_df.replace({np.nan: ""})
#             # Import committees/filers using query builder
#             logger.info("Importing {} filers", len(filers_df))
#             for _, row in filers_df.iterrows():
#                 print(row["FILER_NAME"])
#                 (
#                     merge()
#                     .node(
#                         labels="Filer",
#                         id=uuid.uuid4(),
#                         filer_id=str(row["FILER_ID"]),
#                         name=row["FILER_NAME"],
#                         type=row["FILER_TYPE_DESC"],
#                         status=row["FILER_STATUS"],
#                         # office=row['OFFICE_DESC'],
#                         # district=row['DISTRICT'],
#                         # county=row['COUNTY_DESC']
#                     )
#                     .execute()
#                 )
#
#             # Data cleanup for contributions
#             logger.info("Importing donors and contributions")
#             # contributions_df['SCHED_DATE'] = pd.to_datetime(contributions_df['SCHED_DATE'])
#             contributions_df = contributions_df.replace({np.nan: ""})
#
#             for i, row in contributions_df.iterrows():
#                 try:
#                     donor_id = self.generate_donor_id(row)
#                     donor_type = (
#                         "Organization"
#                         if pd.isna(row["FLNG_ENT_FIRST_NAME"])
#                         else "Individual"
#                     )
#                     donor_name = (
#                         self.clean_name(row["FLNG_ENT_NAME"])
#                         if donor_type == "Organization"
#                         else f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#                     )
#
#                     # Create or merge donor using query builder
#                     (
#                         merge()
#                         .node(
#                             labels="Donor",
#                             id=donor_id,
#                             name=donor_name,
#                             type=donor_type,
#                             address=row["FLNG_ENT_ADD1"],
#                             city=row["FLNG_ENT_CITY"],
#                             state=row["FLNG_ENT_STATE"],
#                             zip=row["FLNG_ENT_ZIP"],
#                         )
#                         .execute()
#                     )
#
#                     # Create contribution and relationships using query builder
#                     (
#                         create()
#                         .match()
#                         .node(labels="Donor", id=donor_id, variable="d")
#                         .match()
#                         .node(
#                             labels="Filer", filer_id=str(row["FILER_ID"]), variable="f"
#                         )
#                         .create()
#                         .node(
#                             labels="Contribution",
#                             variable="t",
#                             transaction_id=row["TRANS_NUMBER"],
#                             amount=float(row["ORG_AMT"]),
#                             date=row["SCHED_DATE"],
#                             payment_type=row["PAYMENT_TYPE_DESC"],
#                             contributor_type=row["CNTRBR_TYPE_DESC"],
#                             payment_method=row["PAYMENT_TYPE_DESC"],
#                         )
#                         .relationship(variable="r1", type="MADE")
#                         .from_node("d")
#                         .to_node("t")
#                         .relationship(variable="r2", type="TO")
#                         .from_node("t")
#                         .to_node("f")
#                         .execute()
#                     )
#
#                     if (i + 1) % 100 == 0:
#                         logger.debug(f"Processed {i + 1} contributions")
#
#                 except Exception as e:
#                     logger.error(
#                         f"Error processing contribution {row['TRANS_NUMBER']}: {str(e)}"
#                     )
#                     raise
#
#             # for i, row in filers_df.iterrows():
#             #     try:
#             #
#             #         query = create().node(labels="Filer",
#             #                               filer_id=row['FILER_ID'],
#             #                                 name=row['FILER_NAME'],
#             #                                 type=row['FILER_TYPE_DESC'],
#             #                                 status=row['FILER_STATUS'],
#             #                                 office=row['OFFICE_DESC'],
#             #                                 district=row['DISTRICT'],
#             #                                 county=row['COUNTY_DESC'],
#             #                                 municipality=row['MUNICIPALITY'],
#             #                                 subdivision=row['SUBDIVISION'],
#             #                                 variable='f').return_().limit(1).execute()
#             #
#             #         node = list(query)[0]
#             #         print(node._id)
#             #         if (i + 1) % 100 == 0:
#             #             logger.debug(f"Processed {i+1} filers")
#             #     except Exception as e:
#             #         logger.error("Error importing committee %s: %s",
#             #                         row['FILER_ID'], str(e))
#             #         raise
#             #
#             # logger.info("Importing donors and contributions")
#             #
#             # ## Data cleanup
#             #
#             # # Parse date strings into python datetime objects
#             # contributions_df['SCHED_DATE'] = pd.to_datetime(contributions_df['SCHED_DATE'])
#             # # Change NaN to None, interpreted as null by neo4j
#             # contributions_df = contributions_df.replace({np.nan: None})
#             #
#             # for i, row in contributions_df.iterrows():
#             #     try:
#             #         donor_id = self.generate_donor_id(row)
#             #
#             #         if pd.isna(row['FLNG_ENT_FIRST_NAME']):
#             #             donor_type = 'Organization'
#             #             donor_name = self.clean_name(row['FLNG_ENT_NAME'])
#             #         else:
#             #             donor_type = 'Individual'
#             #             donor_name = f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#             #
#             #         # Create or merge donor
#             #
#             #         query = create().node(labels="Donor",
#             #                               id=donor_id,
#             #                               name=donor_name,
#             #                               type=donor_type,
#             #                               address=row['FLNG_ENT_ADD1'],
#             #                               city=row['FLNG_ENT_CITY'],
#             #                               state=row['FLNG_ENT_STATE'],
#             #                               zip=row['FLNG_ENT_ZIP']
#             #                               ).execute()
#             #         #
#             #         # # Create contribution node
#             #         #
#             #         query = create().node(labels="Contribution",
#             #                               id=uuid.uuid4(),
#             #                               transaction_id=row['TRANS_NUMBER'],
#             #                               amount=float(row['ORG_AMT']),
#             #                               date=row['SCHED_DATE'],
#             #                               payment_type=row['PAYMENT_TYPE_DESC'],
#             #                               contributor_type=row['CNTRBR_TYPE_DESC'],
#             #                               payment_method=row['PAYMENT_TYPE_DESC']
#             #                               ).execute()
#             #
#             #         query = (create().node(labels="Donor",
#             #                               id=donor_id,
#             #                               name=donor_name,
#             #                               type=donor_type,
#             #                               address=row['FLNG_ENT_ADD1'],
#             #                               city=row['FLNG_ENT_CITY'],
#             #                               state=row['FLNG_ENT_STATE'],
#             #                               zip=row['FLNG_ENT_ZIP']
#             #                               ).to(relationship_type="Made")
#             #                             .node(labels="Contribution",
#             #                               transaction_id=row['TRANS_NUMBER'],
#             #                               amount=float(row['ORG_AMT']),
#             #                               date=row['SCHED_DATE'],
#             #                               payment_type=row['PAYMENT_TYPE_DESC'],
#             #                               contributor_type=row['CNTRBR_TYPE_DESC'],
#             #                               payment_method=row['PAYMENT_TYPE_DESC']
#             #                               ).execute())
#             #         #
#             #         # # Create relationships
#             #         # Made(_start_node_id=donor._id, _end_node_id=contribution._id).save(self.db)
#             #         # To(_start_node_id=contribution._id, _end_node_id=Filer(filer_id=str(row['FILER_ID']))._id).save(self.db)
#             #
#             #         if (i + 1) % 100 == 0:
#             #             logger.debug(f"Processed {i + 1} contributions")
#             #     except Exception as e:
#             #         logger.error("Error importing contribution %s: %s",
#             #                         row['TRANS_NUMBER'], str(e))
#             #         raise
#
#             logger.success("Data import completed successfully")
#
#         except Exception as e:
#             logger.error("Fatal error during data import: %s", str(e))
#             raise
#
#     def import_data_unwind(self, filers_df: pd.DataFrame):
#         logger.info("Starting bulk data import")
#
#         try:
#             # Import filers using bulk save
#             logger.info("Importing {} filers", len(filers_df))
#             Filer.bulk_save(filers_df, self.db)
#
#             # Prepare donor data
#             logger.info("Preparing donor data")
#             contributions_df["donor_type"] = contributions_df[
#                 "FLNG_ENT_FIRST_NAME"
#             ].apply(lambda x: "Individual" if not pd.isna(x) else "Organization")
#
#             contributions_df["donor_name"] = contributions_df.apply(
#                 lambda row: (
#                     f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#                     if row["donor_type"] == "Individual"
#                     else self.clean_name(row["FLNG_ENT_NAME"])
#                 ),
#                 axis=1,
#             )
#
#             contributions_df["donor_id"] = contributions_df.apply(
#                 self.generate_donor_id, axis=1
#             )
#
#             # Get unique donors
#             unique_donors = contributions_df.drop_duplicates(subset=["donor_id"])
#
#             # Import donors using bulk save
#             logger.info("Importing {} donors", len(unique_donors))
#             Donor.bulk_save(unique_donors, self.db)
#
#             # Import contributions with relationships using bulk save
#             logger.info(
#                 "Importing {} contributions with relationships", len(contributions_df)
#             )
#             Contribution.bulk_save_with_relationships(contributions_df, self.db)
#
#             logger.success("Bulk data import completed successfully")
#
#         except Exception as e:
#             logger.error(f"Fatal error during bulk import: {str(e)}")
#             raise
#
#     """ Import data using LOAD CSV Cypher clause, which should be one of the fastest methods.
#         Currently requires manual intervention.
#     """
#
#     def import_data_from_csv(
#         self, contributions_df: pd.DataFrame, filers_df: pd.DataFrame
#     ):
#         """Import data using LOAD CSV Cypher clause"""
#         logger.info("Starting CSV data import")
#
#         try:
#             # Create temporary directory for CSV files
#             with tempfile.TemporaryDirectory() as temp_dir:
#                 # Save filers to CSV
#                 filers_path = Path.cwd() / "data" / "filers.csv"
#                 filers_df.to_csv(filers_path, index=False)
#
#                 # Process and save donors/contributions
#                 contributions_df["donor_type"] = contributions_df[
#                     "FLNG_ENT_FIRST_NAME"
#                 ].apply(lambda x: "Individual" if not pd.isna(x) else "Organization")
#
#                 contributions_df["donor_name"] = contributions_df.apply(
#                     lambda row: (
#                         f"{row['FLNG_ENT_FIRST_NAME']} {row['FLNG_ENT_LAST_NAME']}".strip()
#                         if row["donor_type"] == "Individual"
#                         else self.clean_name(row["FLNG_ENT_NAME"])
#                     ),
#                     axis=1,
#                 )
#
#                 contributions_df["donor_id"] = contributions_df.apply(
#                     self.generate_donor_id, axis=1
#                 )
#
#                 # Get unique donors and save to CSV
#                 unique_donors = contributions_df[
#                     [
#                         "donor_id",
#                         "donor_name",
#                         "donor_type",
#                         "FLNG_ENT_ADD1",
#                         "FLNG_ENT_CITY",
#                         "FLNG_ENT_STATE",
#                         "FLNG_ENT_ZIP",
#                     ]
#                 ].drop_duplicates(subset=["donor_id"])
#                 donors_path = Path.cwd() / "data" / "donors.csv"
#                 unique_donors.to_csv(donors_path, index=False)
#
#                 # Save contributions to CSV
#                 contributions_path = Path.cwd() / "data" / "contributions.csv"
#                 contributions_df.to_csv(contributions_path, index=False)
#                 print(contributions_path)
#                 # Import filers
#                 logger.info("Importing {} filers", len(filers_df))
#                 self.db.execute("""
#                     LOAD CSV FROM "/var/lib/memgraph/remote-data/filers.csv" WITH HEADER AS row
#                     MERGE (f:Filer {filer_id: row.FILER_ID})
#                     SET
#                         f.id = {},
#                         f.name = row.FILER_NAME,
#                         f.type = row.FILER_TYPE_DESC,
#                         f.status = row.FILER_STATUS,
#                         f.office = row.OFFICE_DESC,
#                         f.district = row.DISTRICT,
#                         f.county = row.COUNTY_DESC
#                 """).format(str(uuid.uuid4()))
#
#                 # Import donors
#                 logger.info("Importing {} donors", len(unique_donors))
#                 self.db.execute(
#                     """
#                     LOAD CSV WITH HEADERS FROM 'file:///{}' AS row
#                     MERGE (d:Donor {id: row.donor_id})
#                     SET
#                         d.name = row.donor_name,
#                         d.type = row.donor_type,
#                         d.address = row.FLNG_ENT_ADD1,
#                         d.city = row.FLNG_ENT_CITY,
#                         d.state = row.FLNG_ENT_STATE,
#                         d.zip = row.FLNG_ENT_ZIP
#                 """.format(donors_path.replace("\\", "/"))
#                 )
#
#                 # Import contributions with relationships
#                 logger.info(
#                     "Importing {} contributions with relationships",
#                     len(contributions_df),
#                 )
#                 self.db.execute(
#                     """
#                     LOAD CSV WITH HEADERS FROM 'file:///{}' AS row
#                     MATCH (d:Donor {id: row.donor_id})
#                     MATCH (f:Filer {filer_id: row.FILER_ID})
#                     CREATE (d)-[:MADE]->(c:Contribution {
#                         transaction_id: row.TRANS_NUMBER,
#                         amount: toFloat(row.ORG_AMT),
#                         date: datetime(row.SCHED_DATE),
#                         payment_type: row.PAYMENT_TYPE_DESC,
#                         contributor_type: row.CNTRBR_TYPE_DESC,
#                         payment_method: row.PAYMENT_TYPE_DESC
#                     })-[:TO]->(f)
#                 """.format(contributions_path.replace("\\", "/"))
#                 )
#
#                 logger.success("CSV data import completed successfully")
#
#         except Exception as e:
#             logger.error(f"Fatal error during CSV import: {str(e)}")
#             raise
#
#
# if __name__ == "__main__":
#     contributions_df = pd.read_csv(Path.cwd() / "data" / "cf_data.csv", escapechar="\\")
#     filers_df = pd.read_csv(Path.cwd() / "data" / "cf_filers.csv", escapechar="\\")
#
#     uri = f"bolt://localhost:7687"
#     username = ""
#     password = ""
#
#     contributions_df["ID"] = contributions_df.apply(lambda _: str(uuid.uuid4()), axis=1)
#
#     db = DonorGraph(host="localhost", port=7687, username="", password="")
#     db.setDriver(uri, username, password)
#     db.clear_database()
#     db.import_data(contributions_df, filers_df)
#     # db.import_data_from_query_builder(contributions_df, filers_df)
#     # db.import_data_unwind(filers_df)
#     # db.import_data_from_csv(contributions_df, filers_df)
#     db.close()
