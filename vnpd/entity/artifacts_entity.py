from dataclasses import dataclass

# Data Ingestion Artifacts
@dataclass
class DataIngestionArtifacts:
    image_data_dir: str

@dataclass
class DataTransformationArtifacts:
    transformed_data_file_path:str
    transformed_output_file_path:str