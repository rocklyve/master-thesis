from study_02.src.hrv_pipeline import HRVPipeline

if __name__ == "__main__":
    file_path = "2023-09-28 11-31-05.txt"  # Ändern Sie dies entsprechend dem Dateipfad

class Study2Pipeline:
    # init
    def __init__(self):
        pass

    def execute(self):
        folder_path = "data/test"
        target_folder = "target"

        pipeline = HRVPipeline(folder_path, target_folder)
        pipeline.process_files()

if __name__ == "__main__":
    Study2Pipeline().execute()