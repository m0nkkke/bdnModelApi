const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const resultImage = document.getElementById("resultImage");

fileInput.addEventListener("change", () => {
  uploadBtn.disabled = fileInput.files.length === 0;
});

uploadBtn.addEventListener("click", async () => {
  if (!fileInput.files.length) return;

  uploadBtn.textContent = "Загружаем...";
  uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const resp = await fetch("/predict/image", {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) throw new Error(resp.statusText);

    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    resultImage.src = url;
  } catch (err) {
    alert("Ошибка при распознавании: " + err.message);
  } finally {
    uploadBtn.textContent = "Загрузить и распознать";
    uploadBtn.disabled = false;
  }
});
