def parsehtml(allmessages,memberid,membername,memberjoin,memberavatar):
    htmlbase = f'<!DOCTYPE html><script>var socket = new WebSocket(\'ws://localhost:8765\');function kickPlayer(){{socket.send("{memberid}");}}</script><a href="../home.html"><button id="jumpback"><<</button></a><a><button onclick="kickPlayer()" id="kick">kick</button></a><header><img src="{memberavatar}"><link href="../StyleSheet2.css" rel="stylesheet"/><h1>{membername}</h1><h5>{memberid}</h5><div id="userinfo"><p>Join date: {memberjoin}</p></div></header><body><div id="messages"><h2>Last 50 messages</h2>'

    for index, i in enumerate(allmessages):
        htmlbase += (f'<div><img src="{memberavatar}"><p>{allmessages[index][0]} : {allmessages[index][1]}</p></div>')

    htmlbase += ('</div></body><footer></footer>')

    with open(f'CRAB/html/{memberid}.html','w',encoding='utf-8') as f:
        f.write(htmlbase)

