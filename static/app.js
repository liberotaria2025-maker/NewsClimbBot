// JavaScript para el Bot de Twitter
document.addEventListener('DOMContentLoaded', function() {
    console.log('Bot de Twitter - Aplicación iniciada');
    
    // Inicializar componentes
    initializeApp();
    
    // Auto-actualización cada 5 minutos
    setInterval(updateDashboard, 300000);
});

/**
 * Inicializar la aplicación
 */
function initializeApp() {
    // Configurar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar eventos
    setupEventListeners();
    
    // Validar formularios
    setupFormValidation();
    
    // Actualizar timestamp
    updateTimestamp();
}

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Botones de test de tweet
    const testButtons = document.querySelectorAll('form[action*="test_tweet"] button');
    testButtons.forEach(button => {
        button.addEventListener('click', function() {
            showLoadingState(this);
        });
    });
    
    // Botón de actualizar stats
    const refreshBtn = document.querySelector('[onclick="refreshStats()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            updateDashboard();
        });
    }
    
    // Formulario de configuración
    const configForm = document.querySelector('form[action*="config"]');
    if (configForm) {
        configForm.addEventListener('submit', function() {
            showLoadingOverlay('Guardando configuración...');
        });
    }
}

/**
 * Configurar validación de formularios
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Validación en tiempo real para campos requeridos
    const requiredInputs = document.querySelectorAll('input[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

/**
 * Validar un campo específico
 */
function validateField(field) {
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
    
    return isValid;
}

/**
 * Mostrar estado de carga en un botón
 */
function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Procesando...';
    button.disabled = true;
    
    // Restaurar después de 3 segundos si no hay redirección
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

/**
 * Mostrar overlay de carga
 */
function showLoadingOverlay(message = 'Cargando...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    overlay.style.zIndex = '9999';
    
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <div>${message}</div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Auto-remover después de 10 segundos
    setTimeout(() => {
        hideLoadingOverlay();
    }, 10000);
}

/**
 * Ocultar overlay de carga
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Actualizar dashboard con datos en tiempo real
 */
async function updateDashboard() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error('Error al obtener estadísticas');
        }
        
        const data = await response.json();
        
        // Actualizar contadores si existen los elementos
        updateCounterIfExists('total-tweets', data.total_tweets);
        updateCounterIfExists('today-tweets', data.today_tweets);
        updateCounterIfExists('success-rate', data.success_rate + '%');
        
        // Actualizar último tweet
        if (data.last_tweet) {
            updateLastTweet(data.last_tweet);
        }
        
        // Actualizar timestamp
        updateTimestamp();
        
        console.log('Dashboard actualizado:', data);
        
    } catch (error) {
        console.error('Error actualizando dashboard:', error);
        showNotification('Error al actualizar datos', 'error');
    }
}

/**
 * Actualizar contador si el elemento existe
 */
function updateCounterIfExists(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Animación de conteo
        animateCounter(element, parseInt(element.textContent) || 0, value);
    }
}

/**
 * Animar contador
 */
function animateCounter(element, start, end) {
    const duration = 1000; // 1 segundo
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Actualizar información del último tweet
 */
function updateLastTweet(tweetData) {
    const lastTweetElement = document.getElementById('last-tweet');
    if (lastTweetElement) {
        lastTweetElement.innerHTML = `
            <div class="d-flex justify-content-between">
                <div class="flex-grow-1">
                    <p class="mb-1">${tweetData.content}</p>
                    <small class="text-muted">
                        <i class="fas fa-tag me-1"></i>${tweetData.type}
                        <i class="fas fa-clock ms-3 me-1"></i>${tweetData.posted_at}
                    </small>
                </div>
            </div>
        `;
    }
}

/**
 * Actualizar timestamp
 */
function updateTimestamp() {
    const timestampElement = document.getElementById('last-update');
    if (timestampElement) {
        const now = new Date();
        const formatted = now.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        timestampElement.textContent = formatted;
    }
}

/**
 * Mostrar notificación
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Exportar logs (placeholder)
 */
function exportLogs() {
    showLoadingOverlay('Preparando exportación...');
    
    // Simular exportación
    setTimeout(() => {
        hideLoadingOverlay();
        showNotification('Funcionalidad de exportación en desarrollo', 'info');
    }, 2000);
}

/**
 * Probar conexiones de APIs (placeholder)
 */
function testConnections() {
    showLoadingOverlay('Probando conexiones...');
    
    // Simular prueba de conexiones
    setTimeout(() => {
        hideLoadingOverlay();
        showNotification('Funcionalidad de prueba de conexiones en desarrollo', 'info');
    }, 3000);
}

/**
 * Utilidades para manejo de errores
 */
window.addEventListener('error', function(event) {
    console.error('Error JavaScript:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Promise rechazada:', event.reason);
});

/**
 * Detectar cambios de conectividad
 */
window.addEventListener('online', function() {
    showNotification('Conexión restaurada', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Sin conexión a internet', 'warning');
});

/**
 * Funciones globales para compatibilidad
 */
window.refreshStats = updateDashboard;
window.exportLogs = exportLogs;
window.testConnections = testConnections;

// Auto-actualizar timestamp cada minuto
setInterval(updateTimestamp, 60000);

console.log('JavaScript del bot inicializado correctamente');
