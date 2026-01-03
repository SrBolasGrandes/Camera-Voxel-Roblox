navigator.mediaDevices.getUserMedia({video:true})
.then(s=>{
    const v=document.querySelector("video")
    v.srcObject=s
    const c=document.createElement("canvas")
    const x=c.getContext("2d")

    setInterval(()=>{
        c.width=96;c.height=96
        x.drawImage(v,0,0,96,96)
        c.toBlob(b=>{
            fetch("/cameraSend",{method:"POST",body:b})
        })
    },50)
})
