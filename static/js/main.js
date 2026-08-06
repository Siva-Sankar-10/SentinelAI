// =========================================
// SentinelAI Main JavaScript
// =========================================
(function () {

    if (window.AOS && typeof window.AOS.init === "function") {
        window.AOS.init({
            duration: 1000,
            once: false
        });
    }

// ==========================
// Live Clock
// ==========================

function updateClock(){

    const now = new Date();
    const dateEl = document.getElementById("date");
    const clockEl = document.getElementById("clock");

    if (dateEl) {
        dateEl.innerHTML = now.toLocaleDateString('en-IN', {
            weekday:'long',
            year:'numeric',
            month:'long',
            day:'numeric'
        });
    }

    if (clockEl) {
        clockEl.innerHTML = now.toLocaleTimeString('en-IN');
    }

}

setInterval(updateClock,1000);

updateClock();

// ==========================
// Typing Animation
// ==========================

const typingEl = document.getElementById("typing");

if (typingEl && window.Typed) {
    new Typed("#typing",{

        strings:[

            "AI Powered Defense Command Center",

            "Random Forest Detection Engine",

            "Machine Learning Threat Analysis",

            "Intelligent Network Monitoring"

        ],

        typeSpeed:60,

        backSpeed:35,

        backDelay:1800,

        loop:true

    });
}

// ==========================
// Animated Counter
// ==========================

function animateValue(id,start,end,duration){

    let obj=document.getElementById(id);

    if(!obj) return;

    let range=end-start;

    let current=start;

    let increment=end>start?1:-1;

    let stepTime=Math.abs(Math.floor(duration/range));

    let timer=setInterval(function(){

        current+=increment;

        obj.innerHTML=current+"%";

        if(current==end){

            clearInterval(timer);

        }

    },stepTime);

}

animateValue("accuracy",0,99,2500);

// ==========================
// Navbar Scroll Effect
// ==========================

const nav=document.querySelector(".navbar");

window.addEventListener("scroll",function(){

    if (!nav) return;

    if(window.scrollY>50){

        nav.style.background="rgba(0,0,0,.90)";

        nav.style.boxShadow="0 0 25px rgba(212,175,55,.25)";

    }

    else{

        nav.style.background="rgba(0,0,0,.60)";

        nav.style.boxShadow="none";

    }

});

// ==========================
// Mouse Glow
// ==========================

const existingGlow=document.querySelector(".mouse-glow");

if (!existingGlow && document.body) {
    const glow=document.createElement("div");
    glow.className="mouse-glow";
    document.body.appendChild(glow);
}

document.addEventListener("mousemove",(e)=>{

    const glow=document.querySelector(".mouse-glow");

    if (!glow) return;

    glow.style.left=e.clientX+"px";

    glow.style.top=e.clientY+"px";

});

// ==========================
// Floating Status Animation
// ==========================

const cards=document.querySelectorAll(".status-card");

cards.forEach((card,index)=>{

    card.style.animation=`floatCard 3s ease-in-out ${index*0.3}s infinite`;

});

// ==========================
// AI Terminal Typing
// ==========================

const terminal=document.querySelector(".terminal");

const logs=[

"> AI Engine Initialized",

"> Random Forest Loaded",

"> Dataset Ready",

"> Prediction Service Active",

"> Waiting For Upload..."

];

let i=0;

setInterval(()=>{

    if(!terminal) return;

    if(i>=logs.length) return;

    let p=document.createElement("p");

    p.innerHTML=logs[i];

    terminal.appendChild(p);

    terminal.scrollTop=terminal.scrollHeight;

    i++;

},2000);

// ==========================
// Particle Background
// ==========================

particlesJS("particles-js",{

"particles":{

"number":{

"value":80

},

"color":{

"value":"#D4AF37"

},

"shape":{

"type":"circle"

},

"opacity":{

"value":0.5

},

"size":{

"value":3

},

"line_linked":{

"enable":true,

"distance":160,

"color":"#D4AF37",

"opacity":0.25,

"width":1

},

"move":{

"enable":true,

"speed":2

}

},

"interactivity":{

"events":{

"onhover":{

"enable":true,

"mode":"grab"

}

},

"modes":{

"grab":{

"distance":180,

"line_linked":{

"opacity":0.7

}

}

}

}

});

})();