const container = document.querySelector(".ai-core");

if(container){

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
45,
container.clientWidth/container.clientHeight,
0.1,
1000
);

const renderer = new THREE.WebGLRenderer({
alpha:true,
antialias:true
});

renderer.setSize(
container.clientWidth,
container.clientHeight
);

container.appendChild(renderer.domElement);

// Sphere

const geometry = new THREE.SphereGeometry(2,64,64);

const material = new THREE.MeshBasicMaterial({

wireframe:true,

color:0xFFD700

});

const sphere = new THREE.Mesh(
geometry,
material
);

scene.add(sphere);

// Outer Ring

const ringGeometry = new THREE.TorusGeometry(
2.8,
0.03,
16,
100
);

const ringMaterial = new THREE.MeshBasicMaterial({

color:0xD4AF37

});

const ring = new THREE.Mesh(
ringGeometry,
ringMaterial
);

scene.add(ring);

camera.position.z=6;

function animate(){

requestAnimationFrame(animate);

sphere.rotation.y+=0.004;

sphere.rotation.x+=0.002;

ring.rotation.x+=0.01;

ring.rotation.y+=0.005;

renderer.render(scene,camera);

}

animate();

}