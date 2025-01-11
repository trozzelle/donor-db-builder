# from typing import Optional, List, Dict, Any
# import duckdb
# import pyarrow as arrow
# from pathlib import Path
# import json
# from datetime import datetime
# import uuid
# from sqlmodel import create_engine, SQLModel, Session, select
# from sqlalchemy import URL
# from .models_orm import WebContent, ContentMetadata
# from loguru import logger
#
# MODULE_DIR = Path(__file__).parent.parent.parent
# DEFAULT_DB_PATH = MODULE_DIR / "data" / "content.duckdb"
#
#
# class ContentStore:
#     """Manages storage of web content"""
#
#     def __init__(self, db_path: str = None):
#         if db_path is None:
#             db_path = DEFAULT_DB_PATH
#
#         self.db_path = db_path
#
#         engine = create_engine(f"duckdb:///{db_path}", echo=True)
#
#         self.engine = engine
#
#         # self.conn = duckdb.connect(database=db_path)
#         self._initialize_db()
#
#     def _initialize_db(self):
#         """Initialize schema if they don't exist"""
#         SQLModel.metadata.create_all(self.engine)
#         # self.conn.execute("""
#         #     CREATE TABLE IF NOT EXISTS content (
#         #     id VARCHAR PRIMARY KEY,
#         #     url VARCHAR NOT NULL,
#         #     domain VARCHAR,
#         #     title VARCHAR,
#         #     content TEXT,
#         #     metadata JSON,
#         #     fetched_at TIMESTAMP,
#         #     donor_id VARCHAR,
#         #     tags JSON,
#         #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         #     );
#         #
#         #     CREATE INDEX IF NOT EXISTS idx_content_donor ON content (donor_id);
#         #     CREATE INDEX IF NOT EXISTS idx_content_domain ON content (domain);
#         # """)
#
#     def store_content(
#         self,
#         content: Dict[str, Any],
#         donor_id: Optional[str] = None,
#         tags: Optional[List[str]] = None,
#     ):
#         """Store content in database"""
#
#         content_id = str(uuid.uuid4())
#         session = Session(self.engine)
#
#         try:
#             record = WebContent(
#                 uid=content_id,
#                 url=content["url"],
#                 domain=content["domain"],
#                 title=content.get("title"),
#                 content=content["content"],
#                 site_meta=json.dumps(content.get("metadata", {})),
#                 fetched_at=content["fetched_at"],
#                 donor_id=donor_id,
#                 tags=json.dumps(tags or []),
#             )
#             session.add(record)
#             session.commit()
#
#             return content_id
#
#         except Exception as e:
#             logger.error(f"Failed to store content {str(e)}")
#             raise
#
#     def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
#         """Retrieve content from database"""
#
#         with Session(self.engine) as session:
#             statement = select(WebContent).where(WebContent.uid == content_id)
#             result = session.exec(statement).first()
#
#             if result:
#                 return dict(result)
#             return None
#
#     def get_donor_content(self, donor_id: str) -> List[Dict[str, Any]]:
#         """Retrieve all content associated with a donor"""
#
#         with Session(self.engine) as session:
#             statement = select(WebContent).where(WebContent.donor_id == donor_id)
#             results = session.exec(statement)
#
#             if results:
#                 return [dict(result) for result in results]
#             return None
#
#     def export_to_arrow(self, output_path: str):
#         """Export content to Arrow format
#         # TODO Update this for SQLAlchemy"""
#         # with Session(self.engine) as session:
#         #     statement = select(WebContent)
#         #     results = session.exec(statement)
#         #     if results:
#
#         query_results = self.conn.execute("SELECT * FROM content").arrow()
#         arrow.parquet.write_table(query_results, output_path)
