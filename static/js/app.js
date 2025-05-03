const fileInput = document.getElementById("fileInput");
const uploadBtn  = document.getElementById("uploadBtn");
const resultImage = document.getElementById("resultImage");
const resultText  = document.getElementById("resultText");

fileInput.addEventListener("change", () => {
  uploadBtn.disabled = !fileInput.files.length;
});

uploadBtn.addEventListener("click", async () => {
  if (!fileInput.files.length) return;

  uploadBtn.textContent = "Распознаю...";
  uploadBtn.disabled = true;
  resultImage.src = "";
  resultText.textContent = "";

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    // 1) Получаем JSON
    const respJson = await fetch("/predict", {
      method: "POST",
      body: formData
    });
    if (!respJson.ok) throw new Error(await respJson.text());

    const data = await respJson.json();

    // Формируем читаемый текст
    let txt = "";
    if (data.barcodes && data.barcodes.length) {
      txt += `Barcode: ${data.barcodes.join(", ")}\n`;
    }
    data.items.forEach((it, idx) => {
      // в зависимости от поля expiry или confidence
      const dateOrConf = it.expiry ?? it.confidence ?? "";
      txt += `Item ${idx+1}:\n  Name: ${it.name}\n  Date/Conf: ${dateOrConf}\n  BBox: [${it.bbox.map(n=>n.toFixed(1)).join(", ")}]\n\n`;
    });
    resultText.textContent = txt.trim();

    // 2) Получаем аннотированную картинку
    const respImg = await fetch("/predict/image", {
      method: "POST",
      body: formData
    });
    if (!respImg.ok) throw new Error("Не удалось получить картинку");
    const blob = await respImg.blob();
    resultImage.src = URL.createObjectURL(blob);

  } catch (err) {
    resultText.textContent = "Ошибка: " + err.message;
  } finally {
    uploadBtn.textContent = "Загрузить и распознать";
    uploadBtn.disabled = false;
  }
});
