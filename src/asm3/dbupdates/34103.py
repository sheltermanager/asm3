if asm3.smcom.active():
    # sheltermanager.com only: Final switch over to access old media from S3 instead of filesystem
    execute(dbo,"UPDATE dbfs SET url = replace(url, 'file:', 's3:') where url like 'file:%'")