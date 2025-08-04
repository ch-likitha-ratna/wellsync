
// Flatpickr calendar init
flatpickr(".flatpickr-date", {
  dateFormat: "Y-m-d",
  allowInput: true
});

// Toggle Sub Type visibility
function toggleSubType(select) {
  const subTypeBox = document.getElementById('subTypeContainer');
  subTypeBox.style.display = select.value === 'Paid' ? 'block' : 'none';
}

// Auto-calculate leave duration
function calculateDays() {
  const start = new Date(document.getElementById("start_date").value);
  const end = new Date(document.getElementById("end_date").value);
  const field = document.getElementById("total_days");
  if (!isNaN(start) && !isNaN(end)) {
    const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
    field.value = diff > 0 ? diff : '';
  }
}
