from fastapi import FastAPI, UploadFile, Form
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.tools import Tool
from dotenv import load_dotenv
from pathlib import Path
from fastapi.responses import StreamingResponse
from io import BytesIO
import logging

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

logging.basicConfig(level=logging.INFO)

app = FastAPI()


def get_blob_of_csv(csv_content: str) -> str:
    """
    Write CSV string content to a file blob

    Args:
        csv_content: Csv content that need to be copied in the file.

    Returns:
        The blob object of the csv file

    """

    # Convert the content to a BytesIO object
    file_like = BytesIO(csv_content.encode("utf-8"))

    return file_like


PREFIX_PROMPT = """
You are an AI assistant designed to process user requests. Your task is to:

1. **Process the user's request**: Interpret and understand the user's query or command.
2. **Fetch and organize data**: Based on the user's request, gather the necessary data. This could be in any format, such as CSV, JSON, or text.
3. **Format the result**: Ensure that the data is formatted appropriately based on the user's request:
    - convert it into CSV format
"""


@app.get("/")
def read_root():
    return "I am working guys"


@app.post("/response_csv")
async def csv_response(
    user_command: str = Form(...),
    upload_file: UploadFile = None,
    generateNew: bool = Form(...)
):
    try:
        # Validate the user input
        if user_command is None or upload_file is None or user_command == "":
            raise Exception("Invalid Request, Send All Params!!")

        # Read the uploaded file
        file_content = await upload_file.read()
        file = BytesIO(file_content)

        # Create the agent
        agent = create_csv_agent(
            GoogleGenerativeAI(temperature=0, model="gemini-1.5-flash"),
            file,
            prefix=PREFIX_PROMPT if generateNew else None,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True
        )

        # Invoke the agent with the user command
        response = agent.invoke(user_command)

        # Check if the response contains 'output'
        if 'output' not in response:
            raise Exception("Some error occurred in building the file")

        if generateNew:
            # Process the CSV data if 'generateNew' is True
            cleaned_csv = response['output'].strip().split("```csv")[1].split("```")[0].strip()

            # Convert the cleaned CSV content to a blob for download
            blob = get_blob_of_csv(cleaned_csv)

            # Send the file as a response (Blob content)
            return StreamingResponse(blob, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=output.csv"})

        # If generateNew is False, return the normal response
        return {"output": response['output']}

    except Exception as err:
        logging.error("Error in /response_csv endpoint", exc_info=True)
        return {"error": str(err)}, 500
