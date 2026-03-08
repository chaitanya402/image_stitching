// Centralized JavaScript for GenAI Video Editor UI

const form = document.getElementById('uploadForm')
const filesInput = document.getElementById('files')
const result = document.getElementById('result')

form.addEventListener('submit', async (e) => {
  e.preventDefault()
  const files = filesInput.files
  if (!files || files.length === 0) {
    result.innerText = 'Please select one or more images.'
    return
  }

  const fd = new FormData()
  const desc = document.getElementById('description')
  if (desc && desc.value.trim() !== '') fd.append('description', desc.value.trim())
  for (let i = 0; i < files.length; i++) fd.append('files', files[i])

  result.innerText = 'Uploading...'

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd })
    if (!res.ok) {
      // try to read text for better error messages; JSON may not be available
      const errText = await res.text()
      throw new Error(errText || res.statusText)
    }
    const data = await res.json()

    // Render results
    result.innerHTML = '<h2>Upload Complete</h2>' +
      (data.description ? `<div class="desc"><strong>Description:</strong> ${data.description}</div>` : '') +
      data.uploaded.map(f => `<div class="file">${f.filename} — ${f.size} bytes</div>`).join('')
    // show video (backend may supply a URL or placeholder will be used)
    showVideo(data.video_url)
  } catch (err) {
    result.innerText = 'Upload failed: ' + err.message
  }
})


// after upload completion, show video; fall back to placeholder if none
// this block will be triggered by earlier code above modifying result.innerHTML
const placeholderVideo = 'https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4'
const showVideo = (url) => {
  const src = url || placeholderVideo
  let mediaHtml
  if (src.toLowerCase().endsWith('.gif')) {
    mediaHtml = `<div><h3>Generated Video</h3><img src="${src}" style="max-width:100%"/></div>`
  } else {
    mediaHtml = `<div><h3>Generated Video</h3><video controls src="${src}" style="max-width:100%"></video></div>`
  }
  result.innerHTML += mediaHtml
}

// --- Edit single image / camera capture ---
const editFileInput = document.getElementById('editImageFile')
const editDesc = document.getElementById('editDescription')
const startCameraBtn = document.getElementById('startCamera')
const captureBtn = document.getElementById('capture')
const video = document.getElementById('video')
const canvas = document.getElementById('canvas')

let stream = null

startCameraBtn.addEventListener('click', async (e) => {
  e.preventDefault()
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
    video.style.display = 'none'
    captureBtn.disabled = true
    startCameraBtn.textContent = 'Use Camera'
    return
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.srcObject = stream
    video.style.display = 'block'
    captureBtn.disabled = false
    startCameraBtn.textContent = 'Stop Camera'
  } catch (err) {
    alert('Cannot access camera: ' + err.message)
  }
})

captureBtn.addEventListener('click', async (e) => {
  e.preventDefault()
  // Create a blob from either camera frame or chosen file
  let blob = null
  if (stream) {
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const dataUrl = canvas.toDataURL('image/png')
    const res = await fetch(dataUrl)
    blob = await res.blob()
  } else if (editFileInput.files.length > 0) {
    blob = editFileInput.files[0]
  } else {
    alert('No image selected or camera active')
    return
  }

  const fd = new FormData()
  fd.append('image', blob, 'capture.png')
  if (editDesc && editDesc.value.trim() !== '') fd.append('description', editDesc.value.trim())

  result.innerText = 'Editing image...'

  try {
    const res = await fetch('/api/edit', { method: 'POST', body: fd })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || JSON.stringify(data))

    // Show original (if available) and edited
    let originalHtml = ''
    if (blob) {
      const url = URL.createObjectURL(blob)
      originalHtml = `<div><strong>Original</strong><br/><img src="${url}" style="max-width:320px"/></div>`
    }

    const edited = data.edited_image
    result.innerHTML = '<h2>Edit Result</h2>' + originalHtml + `<div><strong>Edited</strong><br/><img src="${edited}" style="max-width:320px"/></div>`
  } catch (err) {
    result.innerText = 'Edit failed: ' + err.message
  }
})
