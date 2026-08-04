(function () {

    const container = document.querySelector(".ai-core");

    if (!container || typeof window.THREE === "undefined") {
        return;
    }

    const scene = new window.THREE.Scene();

    const camera = new window.THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );

    const renderer = new window.THREE.WebGLRenderer({
        alpha: true,
        antialias: true
    });

    renderer.setSize(
        container.clientWidth,
        container.clientHeight
    );

    container.appendChild(renderer.domElement);

    // Sphere

    const geometry = new window.THREE.SphereGeometry(2, 64, 64);

    const material = new window.THREE.MeshBasicMaterial({
        wireframe: true,
        color: 0xFFD700
    });

    const sphere = new window.THREE.Mesh(
        geometry,
        material
    );

    scene.add(sphere);

    // Outer Ring

    const ringGeometry = new window.THREE.TorusGeometry(
        2.8,
        0.03,
        16,
        100
    );

    const ringMaterial = new window.THREE.MeshBasicMaterial({
        color: 0xD4AF37
    });

    const ring = new window.THREE.Mesh(
        ringGeometry,
        ringMaterial
    );

    scene.add(ring);

    camera.position.z = 6;

    function animate() {
        requestAnimationFrame(animate);

        sphere.rotation.y += 0.004;
        sphere.rotation.x += 0.002;
        ring.rotation.x += 0.01;
        ring.rotation.y += 0.005;

        renderer.render(scene, camera);
    }

    animate();

})();