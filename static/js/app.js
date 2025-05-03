const uploadBtn  = document.getElementById("uploadBtn");
const fileInput  = document.getElementById("fileInput");
const resultImage= document.getElementById("resultImage");
const resultText = document.getElementById("resultText");

fileInput.addEventListener("change", () => {
  uploadBtn.disabled = !fileInput.files.length;
});

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadBtn.textContent = "Распознаю...";
  uploadBtn.disabled = true;
  resultImage.src = "";
  resultText.textContent = "";

  const fd = new FormData();
  fd.append("file", file);

  try {
    // 1) Запрашиваем JSON с распознанными значениями
    const resp = await fetch("/predict", { method: "POST", body: fd });
    if (!resp.ok) throw new Error(await resp.text());
    const { items } = await resp.json();

    let txt = "";
    items.forEach((it, i) => {
      txt += `Item ${i+1}:\n`;
      txt += `  Type:       ${it.type}\n`;
      txt += `  Value:      ${it.value}\n`;
      txt += `  Confidence: ${it.confidence.toFixed(2)}\n\n`;
    });
    resultText.textContent = txt.trim();

    // 3) Получаем аннотированную картинку
    const respImg = await fetch("/predict/image", { method: "POST", body: fd });
    if (!respImg.ok) throw new Error("Не удалось получить картинку");
    const blob = await respImg.blob();
    resultImage.src = URL.createObjectURL(blob);

  } catch(err) {
    resultText.textContent = "Ошибка: " + err.message;
  } finally {
    uploadBtn.textContent = "Загрузить и распознать";
    uploadBtn.disabled = false;
  }
});
