function toggleOptions() {
  var options = document.getElementById("options");
  if (options.style.display === "none" || options.style.display === "") {
    options.style.display = "block"; // Mostrar las opciones
  } else {
    options.style.display = "none"; // Ocultar las opciones
  }
}

//EJEMPLO DE ENVIO DE DATOS, EN PROCESO DE CONSTRUCCION
//TODO HACER COMPROBACIONES DE DATOS CORRECTOS

let folderPath = "";

function selectFolder() {
  const input = document.getElementById("fileInput");
  input.click();
}

function updateFolderPath() {
  const input = document.getElementById("fileInput");
  folderPath = input.files[0].webkitRelativePath.split("/")[0];
  document.getElementById("rutaCarpeta").textContent = folderPath;
}

function toggleOptions() {
  const options = document.getElementById("options");
  options.style.display =
    options.style.display === "none" || options.style.display === ""
      ? "block"
      : "none";
}

async function submitForm(event) {
  event.preventDefault();
  const ancho = document.getElementById("ancho").value;
  const alto = document.getElementById("alto").value;
  const opcion1 = document.getElementById("opcion1").checked;
  const opcion2 = document.getElementById("opcion2").checked;

  const response = await fetch("/submit-form", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      folder_path: folderPath,
      ancho: ancho,
      alto: alto,
      opcion1: opcion1,
      opcion2: opcion2,
    }),
  });

  const data = await response.json();
  console.log("Datos recibidos del servidor:", data);
}
