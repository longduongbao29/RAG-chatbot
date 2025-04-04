
from src.rag.pipeline.Pipeline import Pipeline

pipeline = Pipeline()


print(pipeline.run_pipeline("Viruss có drama gì gần đây???", "test_index"))