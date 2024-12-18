from multiprocessing import Pool, cpu_count
import pandas as pd
from typing import Type, Dict, List, Any, Callable
from gqlalchemy import Node
from loguru import logger
import numpy as np


class ParallelProcessor:
    """
    A generic parallel processing class that handles chunking and parallel execution
    of database operations.
    """

    def __init__(self, num_processes: int = None):
        """
        Initialize the parallel processor.

        Args:
            num_processes: Number of processes to use. Defaults to CPU count.
        """
        self.num_processes = num_processes or cpu_count()

    @staticmethod
    def _process_chunk(args: tuple) -> None:
        """
        Static method to process a single chunk of data.

        Args:
            args: Tuple containing:
                - chunk: DataFrame chunk to process
                - processor_func: Function that processes the chunk
                - db_config: Database configuration dictionary
                - additional_args: Additional arguments for the processor function
        """
        chunk, processor_func, db_config, additional_args = args

        try:
            # Call the provided processor function with the chunk and additional args
            processor_func(chunk=chunk, db_config=db_config, **additional_args)
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            raise

    def process_in_parallel(
            self,
            df: pd.DataFrame,
            processor_func: Callable,
            db_config: Dict[str, Any],
            additional_args: Dict[str, Any] = None,
            chunk_size: int = 1000
    ) -> None:
        """
        Process a DataFrame in parallel using the provided processor function.

        Args:
            df: DataFrame to process
            processor_func: Function that processes each chunk
            db_config: Database configuration dictionary
            additional_args: Additional arguments to pass to the processor function
            chunk_size: Size of each chunk to process
        """
        # # Split dataframe into chunks
        # chunks = np.array_split(df, min(len(df) // chunk_size + 1, self.num_processes))
        #
        # # Prepare chunk data
        # chunk_data = [
        #     (chunk, processor_func, db_config, additional_args or {})
        #     for chunk in chunks
        # ]
        #
        # # Process chunks in parallel
        # with Pool(self.num_processes) as pool:
        #     pool.map(self._process_chunk, chunk_data)

        # Calculate number of chunks based on chunk_size
        num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
        logger.info(f"Processing {len(df)} records in {num_chunks} chunks of {chunk_size}")

        # Split dataframe into chunks of specified size
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

        # Prepare chunk data
        chunk_data = [
            (chunk, processor_func, db_config, additional_args or {})
            for chunk in chunks
        ]

        # Process chunks in parallel using a pool size based on CPU count and chunk count
        pool_size = min(self.num_processes, len(chunks))
        logger.info(f"Using pool size of {pool_size} processes")

        with Pool(pool_size) as pool:
            pool.map(self._process_chunk, chunk_data)