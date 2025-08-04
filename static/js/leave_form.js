// Toggle Sub Type visibility
function toggleSubType() {
  const leaveType = document.querySelector('select[name="leave_type"]').value;
  const subTypeDiv = document.getElementById('subTypeContainer');
  if (subTypeDiv) {
    subTypeDiv.style.display = leaveType === 'Paid' ? 'block' : 'none';
  }
}

// Auto-calculate leave duration
function calculateDays() {
  const startDate = document.getElementById("start_date").value;
  const endDate = document.getElementById("end_date").value;
  const totalDaysField = document.getElementById("total_days");
  
  if (startDate && endDate && totalDaysField) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (!isNaN(start) && !isNaN(end) && end >= start) {
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      totalDaysField.value = diffDays;
    } else {
      totalDaysField.value = '';
    }
  }
}