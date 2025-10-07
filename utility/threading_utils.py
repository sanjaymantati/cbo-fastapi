
import concurrent.futures
from typing import List, Callable, Any, Optional


class ThreadingUtils:
    @staticmethod
    def process_with_threading(
            process_func: Callable[[Any], Any],
            object_list: List[Any],
            max_workers: int = 5,
            **kwargs
    ) -> List[Any]:
        """
        Process a list of objects using threading with a given function

        Args:
            process_func: Function reference to process each object
            object_list: List of objects to process
            max_workers: Maximum number of worker threads
            **kwargs: Additional arguments to pass to the process function

        Returns:
            List of results in the same order as input
        """
        results = []

        with concurrent.futures.ThreadPoolExecutor \
                (max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(process_func, item, **kwargs): idx
                for idx, item in enumerate(object_list)
            }

            # Collect results maintaining order
            temp_results = [None] * len(object_list)
            for future in concurrent.futures.as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                    temp_results[idx] = result
                except Exception as e:
                    temp_results[idx] = f"Error: {e}"

            results = temp_results

        return results