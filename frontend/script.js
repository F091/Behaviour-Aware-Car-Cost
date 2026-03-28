// frontend/script.js

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM Elements - Screens
const landingScreen = document.getElementById('landing-screen');
const formScreen = document.getElementById('form-screen');
const resultsScreen = document.getElementById('results-screen');
const enterBtn = document.getElementById('enter-btn');

// DOM Elements - Form
const registrationInput = document.getElementById('registration');
const annualMileageInput = document.getElementById('annual-mileage');
const fuelPriceInput = document.getElementById('fuel-price');
const cityRatioInput = document.getElementById('city-ratio');
const cityValueDisplay = document.getElementById('city-value');
const drivingStyleBtns = document.querySelectorAll('.style-btn');
const shortTripsSelect = document.getElementById('short-trips');
const calculateBtn = document.getElementById('calculate-btn');
const newSearchBtn = document.getElementById('new-search-btn');
const exportBtn = document.getElementById('export-btn');
const errorMessage = document.getElementById('error-message');
const loadingDiv = document.getElementById('loading');

// State variables
let selectedDrivingStyle = 'normal';
let costChart = null;
let maintenanceChart = null;
let lastResultsData = null;

// Event Listeners - Landing Page
enterBtn.addEventListener('click', handleEnter);

// Event Listeners - Form
calculateBtn.addEventListener('click', handleCalculate);

// Event Listeners - Results
newSearchBtn.addEventListener('click', resetForm);
exportBtn.addEventListener('click', handleExport);

// Update city ratio display when slider changes
cityRatioInput.addEventListener('input', function() {
    cityValueDisplay.textContent = this.value;
});

// Handle driving style button selection
drivingStyleBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        drivingStyleBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedDrivingStyle = this.dataset.style;
    });
});

/**
 * Handle the Enter button click on landing screen.
 * Plays the car animation and transitions to form screen.
 */
function handleEnter() {
    // Get the car element and play animation
    const car = document.querySelector('.car');
    car.classList.add('drive-animation');
    
    // After animation, hide landing and show form
    setTimeout(() => {
        landingScreen.classList.remove('active');
        formScreen.classList.add('active');
        registrationInput.focus();
    }, 1500);
}

/**
 * Validate all required form inputs.
 * Returns true if valid, false otherwise.
 */
function validateForm() {
    // Clear previous error messages
    errorMessage.textContent = '';
    errorMessage.classList.remove('show');

    // Check registration
    if (!registrationInput.value.trim()) {
        showError('Please enter a vehicle registration number');
        return false;
    }

    // Check annual mileage
    if (!annualMileageInput.value || parseInt(annualMileageInput.value) <= 0) {
        showError('Please enter a valid annual mileage');
        return false;
    }

    // Check fuel price
    if (!fuelPriceInput.value || parseFloat(fuelPriceInput.value) <= 0) {
        showError('Please enter a valid fuel price');
        return false;
    }

    return true;
}

/**
 * Display an error message to the user.
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

/**
 * Show the loading spinner.
 */
function showLoading() {
    loadingDiv.classList.remove('hidden');
    calculateBtn.disabled = true;
    calculateBtn.textContent = 'Calculating...';
}

/**
 * Hide the loading spinner.
 */
function hideLoading() {
    loadingDiv.classList.add('hidden');
    calculateBtn.disabled = false;
    calculateBtn.textContent = 'Calculate Cost';
}

/**
 * Call the backend API to estimate ownership costs.
 */
async function estimateOwnershipCost(formData) {
    const url = `${API_BASE_URL}/estimate/ownership/${encodeURIComponent(formData.registration)}`;
    const params = new URLSearchParams({
        annual_mileage: formData.annualMileage,
        fuel_price_per_litre: formData.fuelPrice,
        city_ratio: formData.cityRatio,
        driving_style: formData.drivingStyle,
        short_trip_frequency: formData.shortTripFrequency
    });

    try {
        const response = await fetch(`${url}?${params}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Vehicle registration not found. Please check and try again.');
            }
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

/**
 * Collect form data from input fields.
 */
function getFormData() {
    return {
        registration: registrationInput.value.trim().toUpperCase(),
        annualMileage: parseInt(annualMileageInput.value),
        fuelPrice: parseFloat(fuelPriceInput.value),
        cityRatio: parseInt(cityRatioInput.value),
        drivingStyle: selectedDrivingStyle,
        shortTripFrequency: shortTripsSelect.value
    };
}

/**
 * Format a number as British currency (£).
 */
function formatCurrency(amount) {
    return '£' + amount.toFixed(2);
}

/**
 * Capitalize the first letter of a string.
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Display the results on the page.
 */
function displayResults(data) {
    // Store results for export
    lastResultsData = data;

    // Update header with vehicle name
    document.getElementById('vehicle-name-header').textContent = 
        `${data.make} ${data.model}`;

    // Total cost (most prominent)
    document.getElementById('total-cost-hero').textContent = 
        formatCurrency(data.total_monthly_running_cost);

    // Fuel and Maintenance small cards
    document.getElementById('fuel-cost-detail').textContent = 
        formatCurrency(data.estimated_monthly_fuel_cost);
    document.getElementById('maintenance-cost-detail').textContent = 
        formatCurrency(data.estimated_monthly_maintenance_cost);

    // Vehicle information
    document.getElementById('vehicle-model').textContent = 
        `${data.make} ${data.model}`;
    document.getElementById('vehicle-fuel').textContent = 
        data.fuel_type;
    document.getElementById('vehicle-engine').textContent = 
        `${data.engine_capacity_cc}cc`;

    // Maintenance breakdown
    const breakdown = data.maintenance_breakdown;
    document.getElementById('breakdown-service').textContent = 
        formatCurrency(breakdown.service_monthly);
    document.getElementById('breakdown-tyres').textContent = 
        formatCurrency(breakdown.tyres_monthly);
    document.getElementById('breakdown-brakes').textContent = 
        formatCurrency(breakdown.brakes_monthly);
    document.getElementById('breakdown-major').textContent = 
        formatCurrency(breakdown.major_service_monthly);

    // Driving profile
    const explanation = data.fuel_explanation;
    document.getElementById('profile-city').textContent = 
        `${explanation.city_ratio}%`;
    document.getElementById('profile-style').textContent = 
        capitalize(explanation.driving_style);
    document.getElementById('profile-trips').textContent = 
        capitalize(explanation.short_trip_frequency);

    // Insight summary
    document.getElementById('insight-text').textContent = 
        data.insight_summary;

    // Render charts
    renderCostChart(data);
    renderMaintenanceChart(data);

    // Show results screen
    formScreen.classList.remove('active');
    resultsScreen.classList.add('active');
}

/**
 * Render the cost breakdown doughnut chart.
 */
function renderCostChart(data) {
    // Destroy existing chart if it exists
    if (costChart) {
        costChart.destroy();
    }

    const ctx = document.getElementById('costChart').getContext('2d');
    const fuelCost = data.estimated_monthly_fuel_cost;
    const maintenanceCost = data.estimated_monthly_maintenance_cost;
    
    costChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fuel', 'Maintenance'],
            datasets: [{
                data: [fuelCost, maintenanceCost],
                backgroundColor: [
                    '#f5576c',
                    '#00f2fe'
                ],
                borderColor: ['#ffffff', '#ffffff'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12, weight: 'bold' }
                    }
                }
            }
        }
    });
}

/**
 * Render the maintenance breakdown bar chart.
 */
function renderMaintenanceChart(data) {
    // Destroy existing chart if it exists
    if (maintenanceChart) {
        maintenanceChart.destroy();
    }

    const ctx = document.getElementById('maintenanceChart').getContext('2d');
    const breakdown = data.maintenance_breakdown;
    
    maintenanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Service', 'Tyres', 'Brakes', 'Major Service'],
            datasets: [{
                label: 'Monthly Cost (£)',
                data: [
                    breakdown.service_monthly,
                    breakdown.tyres_monthly,
                    breakdown.brakes_monthly,
                    breakdown.major_service_monthly
                ],
                backgroundColor: [
                    '#3498db',
                    '#9b59b6',
                    '#e67e22',
                    '#1abc9c'
                ],
                borderRadius: 5,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { font: { size: 12, weight: 'bold' } }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '£' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Handle the export button click.
 * Downloads results as JSON file.
 */
function handleExport() {
    if (!lastResultsData) {
        showError('No results to export');
        return;
    }

    // Create export object
    const exportData = {
        timestamp: new Date().toISOString(),
        vehicle: {
            registration: lastResultsData.registration,
            make: lastResultsData.make,
            model: lastResultsData.model,
            year: lastResultsData.year,
            fuel_type: lastResultsData.fuel_type,
            engine_capacity_cc: lastResultsData.engine_capacity_cc
        },
        costs: {
            monthly_fuel_cost: lastResultsData.estimated_monthly_fuel_cost,
            monthly_maintenance_cost: lastResultsData.estimated_monthly_maintenance_cost,
            total_monthly_cost: lastResultsData.total_monthly_running_cost,
            annual_fuel_cost: lastResultsData.estimated_monthly_fuel_cost * 12,
            annual_maintenance_cost: lastResultsData.estimated_monthly_maintenance_cost * 12,
            annual_total_cost: lastResultsData.total_monthly_running_cost * 12
        },
        maintenance_breakdown: {
            service_monthly: lastResultsData.maintenance_breakdown.service_monthly,
            tyres_monthly: lastResultsData.maintenance_breakdown.tyres_monthly,
            brakes_monthly: lastResultsData.maintenance_breakdown.brakes_monthly,
            major_service_monthly: lastResultsData.maintenance_breakdown.major_service_monthly
        },
        driving_profile: {
            city_ratio: lastResultsData.fuel_explanation.city_ratio,
            driving_style: lastResultsData.fuel_explanation.driving_style,
            short_trip_frequency: lastResultsData.fuel_explanation.short_trip_frequency
        },
        insight: lastResultsData.insight_summary
    };

    // Create blob and download
    const jsonString = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `DRIVEWISE-${lastResultsData.registration}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Handle the calculate button click.
 */
async function handleCalculate() {
    // Validate form inputs
    if (!validateForm()) {
        return;
    }

    // Get form data
    const formData = getFormData();

    // Show loading indicator
    showLoading();

    try {
        // Call the API
        const result = await estimateOwnershipCost(formData);
        
        // Hide loading and display results
        hideLoading();
        displayResults(result);
    } catch (error) {
        hideLoading();
        showError(error.message || 'Failed to calculate costs. Please try again.');
    }
}

/**
 * Reset the form to initial state and go back to form screen.
 */
function resetForm() {
    // Clear all inputs
    registrationInput.value = '';
    annualMileageInput.value = '';
    fuelPriceInput.value = '';
    cityRatioInput.value = 0;
    cityValueDisplay.textContent = '0';
    shortTripsSelect.value = 'low';

    // Reset driving style
    selectedDrivingStyle = 'normal';
    drivingStyleBtns.forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-style="normal"]').classList.add('active');

    // Clear error messages
    errorMessage.textContent = '';
    errorMessage.classList.remove('show');

    // Show form screen and hide results
    resultsScreen.classList.remove('active');
    formScreen.classList.add('active');

    // Focus on registration input
    registrationInput.focus();
}

/**
 * Initialize the page on load.
 */
function init() {
    // Set the normal driving style as active by default
    document.querySelector('[data-style="normal"]').classList.add('active');
}

// Initialize when the page loads
window.addEventListener('DOMContentLoaded', init);
