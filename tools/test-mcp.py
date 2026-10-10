"""Read-only smoke check through the actual stdio MCP transport."""
import asyncio,json,sys,os
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    root=Path(__file__).resolve().parents[1]
    params=StdioServerParameters(command=sys.executable,args=[str(root/'tools/vendor/STS2_Mcp/mcp/server.py'),'--host','127.0.0.1','--port','15528','--no-trust-env'])
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            listing=await session.list_tools();assert any(t.name=='get_game_state' for t in listing.tools)
            result=await session.call_tool('get_game_state',{'format':'json'})
            assert not result.isError
            state=json.loads(next(c.text for c in result.content if c.type=='text'))
            assert state['player']['character']=='惠惠（测试）'
            report={'passed':True,'transport':'stdio','tools':len(listing.tools),'state_type':state['state_type'],'character':state['player']['character']}
            output=root/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')/'verification/mcp-smoke.json'
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
