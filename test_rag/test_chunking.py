from src.rag.strategy.chunking.loader.PDFLoader import PDFLoader

loader = PDFLoader("test_rag/Final_QC-dH-_2014_Ban-hanh-25-12-2014.pdf")

print(loader.chunk_text())