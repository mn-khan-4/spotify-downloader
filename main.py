from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
import subprocess

app = FastAPI()

@app.post("/download")
async def download_playlist(playlist_url: str = Form(...)):
    # Unique folder for each request
    temp_id = str(uuid.uuid4())
    output_folder = f"downloads/{temp_id}"
    os.makedirs(output_folder, exist_ok=True)

    # Download playlist with spotdl
    command = f'spotdl {playlist_url} --output "{output_folder}/%(title)s.%(ext)s"'
    result = subprocess.run(command, shell=True)
    
    # Check for success (return error if spotdl fails)
    if result.returncode != 0:
        shutil.rmtree(output_folder)
        return JSONResponse(content={"error": "Download failed! Check your URL."}, status_code=400)

    # Zip the folder
    zip_path = f"{output_folder}.zip"
    shutil.make_archive(output_folder, 'zip', output_folder)

    # Delete the download folder after zipping
    shutil.rmtree(output_folder)

    # Return ZIP file and delete it after sending (streaming)
    response = FileResponse(zip_path, filename="SpotifyPlaylist.zip", media_type='application/zip')
    # Clean up the zip after sending (see below)
    @response.call_on_close
    def cleanup():
        try:
            os.remove(zip_path)
        except Exception:
            pass
    return response
