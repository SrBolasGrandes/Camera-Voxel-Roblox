const g=document.getElementById("g")
const f=document.getElementById("f")

let imgs=JSON.parse(localStorage.getItem("imgs")||"[]")

function save(){localStorage.setItem("imgs",JSON.stringify(imgs))}

function render(){
g.innerHTML=""
imgs.forEach(i=>{
let im=document.createElement("img")
im.src=i
im.width=96
im.onclick=()=>send(i)
g.appendChild(im)
})
}

function send(src){
fetch(src).then(r=>r.blob()).then(b=>{
let fd=new FormData()
fd.append("image",b)
fetch("/fotoSend",{method:"POST",body:fd})
})
}

f.onchange=e=>{
let r=new FileReader()
r.onload=()=>{imgs.push(r.result);save();render()}
r.readAsDataURL(e.target.files[0])
}

render()
