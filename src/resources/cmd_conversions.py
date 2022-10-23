from src.models.cmd import run_cmd


async def echo(args):
    return await run_cmd('echo', args)


async def cat(args):
    return await run_cmd('echo', args, args)