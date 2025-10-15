# OnboardingAndHR-AI-Assistant
An AI-powered employee assistant integrating Groq LLM and RAG via MCP for Claude Desktop. Features include secure employee onboarding, admin IAM for authentication, PDF-based company policy management, and seamless internal query access for employees through a private AI interface.


Steps to run it:

1. Create & activate Python virtual environment, install deps:
cd C:\Users\<you>\code\OnboardingAndHR-AI-Assistant

create venv
python -m venv .venv

activate
.\.venv\Scripts\Activate.ps1

upgrade pip and install packages
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

pip uninstall bcrypt passlib -y
pip install bcrypt==4.1.2 passlib[bcrypt]==1.7.4
Then re-run pip install -r requirements.txt if needed

2. Start Qdrant (Docker):
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

docker ps
you should see the qdrant container running

3. Prepare DB & create initial admin
python create_admin.py

4. Configure Groq API key (optional — for real LLM replies)
$env:GROQ_API_KEY="sk-REPLACE_WITH_YOUR_KEY"

5. Start the FastAPI HTTP server (admin / IAM / upload / ask / admin UI)
uvicorn server:app --reload --port 8000

6. Open these in your browser to confirm:

API docs: http://127.0.0.1:8000/docs

Admin UI (static): http://127.0.0.1:8000/admin/ui

Test endpoints using the Swagger page:

POST /login (use admin@example.com / AdPass123) — returns access_token.

POST /admin/upload_policy — upload a PDF using the token.

GET /admin/users — view registered users (password not shown).

POST /admin/validate/{user_id} — approve users.

7. Upload a policy PDF (admin)

API docs: http://127.0.0.1:8000/docs
POST /login (use admin@example.com / AdPass123) — returns access_token.

http://127.0.0.1:8000/static/admin.html --> upload the document here.

8. Start the FastMCP server (MCP server for Claude Desktop):

python mcp_server.py

9. Install Claude Desktop & configure it to run your MCP server:

Install Claude Desktop

Download & install Claude Desktop for Windows from Anthropic’s official source. (Follow the installer; I can’t provide the installer link here — use Anthropic’s site or the Claude Desktop download you already have.)

Launch Claude Desktop once to create config files.

Add your local MCP server to Claude Desktop config

Open PowerShell and run:
notepad "$env:APPDATA\Claude\claude_desktop_config.json"

Add or edit mcpServers section so it includes your MCP server. Example (use absolute paths):
{
  "mcpServers": {
    "CompanyPolicyAssistant": {
      "command": "C:\\Users\\<you>\\code\\OnboardingAndHR-AI-Assistant\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\<you>\\code\\OnboardingAndHR-AI-Assistant\\mcp_server.py"],
      "env": {},
      "cwd": "C:\\Users\\<you>\\code\\OnboardingAndHR-AI-Assistant"
    }
  }
}
Save the file and fully quit Claude Desktop (right-click tray icon → Quit) then re-open it.

Claude Desktop may prompt once to allow the local tool to run — approve it.

10. Test MCP tool usage inside Claude Desktop

In Claude Desktop, type a prompt instructing the model to use the tool, for example:

Use the tool query_policy to answer: "What is the bereavement leave policy?"

If your MCP server is connected, Claude will make an MCP tool call query_policy → your mcp_server.py executes the RAG pipeline → Groq LLM runs (real or stub) → Claude displays results.

11. How to get your admin’s JWT
Use Swagger UI

Go to http://127.0.0.1:8000/docs

Click on the /login endpoint → “Try it out”

username = admin@example.com
password = AdPass123

Execute → the response will show something like:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....",
  "token_type": "bearer"
}

