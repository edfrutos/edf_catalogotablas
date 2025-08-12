// Dashboard.js - VERSIÓN COMPLETA CON ELIMINACIÓN AUTOMÁTICA
// console.log("🔧 Dashboard.js cargado - VERSIÓN COMPLETA - Timestamp:", new Date().toISOString());

$(function () {
  // console.log("🔧 Inicializando dashboard completo...");

  // Variables globales para Google Drive
  let allBackups = [];
  let selectedBackups = new Set();

  // Variables globales para control de carga
  let isLoadingDriveBackups = false;
  let isLoadingLocalBackups = false;

  // Sistema de eliminación automática de alertas duplicadas
  function removeDuplicateAlerts() {
    const alerts = $('.alert');
    const seenMessages = new Set();

    alerts.each(function () {
      const message = $(this).text().trim();
      if (seenMessages.has(message)) {
        console.log(`🗑️ Eliminando alerta duplicada: ${message}`);
        $(this).remove();
      } else {
        seenMessages.add(message);
      }
    });
  }

  // Función ultra-simple para mostrar alertas
  function showAlert(message, type = "success") {
    console.log(`📢 showAlert: ${message}`);

    // Crear la alerta
    const alertId = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const alert = `
      <div id="${alertId}" class="alert alert-${type} fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" onclick="$(this).closest('.alert').remove()" aria-label="Cerrar"></button>
      </div>
    `;

    $(".container").prepend(alert);

    // Eliminar duplicados inmediatamente
    removeDuplicateAlerts();

    // Auto-eliminar después de 5 segundos
    setTimeout(function () {
      $(`#${alertId}`).fadeOut(500, function () {
        $(this).remove();
      });
    }, 5000);
  }

  // Función para mostrar alertas en el modal de backups locales
  function showModalAlert(message, type = "success") {
    console.log(`📢 showModalAlert: ${message}`);

    // Crear la alerta
    const alertId = `modalAlert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const alert = `
      <div id="${alertId}" class="alert alert-${type} fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" onclick="$(this).closest('.alert').remove()" aria-label="Cerrar"></button>
      </div>
    `;

    // Añadir alerta al modal de backups locales
    $("#localBackupsModal .modal-body").prepend(alert);

    // Auto-eliminar después de 5 segundos
    setTimeout(function () {
      $(`#${alertId}`).fadeOut(500, function () {
        $(this).remove();
      });
    }, 5000);
  }

  // Función para mostrar ventanas emergentes de confirmación
  function showConfirmationModal(title, message, type = "info", autoClose = true) {
    const iconClass = {
      success: "bi-check-circle-fill text-success",
      error: "bi-exclamation-triangle-fill text-danger",
      warning: "bi-exclamation-triangle-fill text-warning",
      info: "bi-info-circle-fill text-info"
    }[type] || "bi-info-circle-fill text-info";

    const modalId = `confirmationModal_${Date.now()}`;

    const modalHtml = `
    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-${type === "success" ? "success" : type === "error" ? "danger" : type === "warning" ? "warning" : "info"} text-white">
            <h5 class="modal-title" id="${modalId}Label">
              <i class="${iconClass} me-2"></i>${title}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">${message}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-circle"></i> Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

    // Añadir modal al DOM
    $("body").append(modalHtml);

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();

    // Auto-cerrar después de 5 segundos si está habilitado
    if (autoClose) {
      setTimeout(() => {
        modal.hide();
      }, 5000);
    }

    // Limpiar modal del DOM cuando se cierre
    document.getElementById(modalId).addEventListener("hidden.bs.modal", function () {
      $(this).remove();
    });
  }

  // Función para mostrar confirmación modal que devuelve una promesa
  function showConfirmDialog(title, message, type = "warning") {
    const modalId = `confirmDialog_${Date.now()}`;

    const modalHtml = `
      <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header bg-${type === "danger" ? "danger" : "warning"} text-white">
              <h5 class="modal-title" id="${modalId}Label">
                <i class="bi bi-question-circle me-2"></i>${title}
              </h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body">
              <p class="mb-0">${message}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="bi bi-x-circle"></i> Cancelar
              </button>
              <button type="button" class="btn btn-${type === "danger" ? "danger" : "warning"}" id="confirmAction">
                <i class="bi bi-check-circle"></i> Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    $("body").append(modalHtml);
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();

    return new Promise((resolve) => {
      $(`#${modalId} #confirmAction`).on("click", function () {
        modal.hide();
        $(`#${modalId}`).remove();
        resolve(true);
      });

      $(`#${modalId}`).on("hidden.bs.modal", function () {
        $(`#${modalId}`).remove();
        resolve(false);
      });
    });
  }

  // Función ultra-simple para ejecutar tareas
  window.runTask = function runTask(task) {
    console.log(`🔧 runTask: ${task}`);

    const btn = $(`.run-task[data-task="${task}"]`);

    // Si el botón ya está deshabilitado, ignorar
    if (btn.prop('disabled')) {
      console.log("⚠️ Botón ya deshabilitado, ignorando");
      return;
    }

    const originalText = btn.html();

    btn.prop("disabled", true)
      .html("<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> Ejecutando...");

    const formData = new FormData();
    formData.append("task", task);

    $.ajax({
      url: "/admin/api/run_task",
      method: "POST",
      data: formData,
      processData: false,
      contentType: false,
      xhrFields: { withCredentials: true },
      success: function (response) {
        console.log("✅ Tarea ejecutada:", response);
        const now = new Date().toLocaleString();
        showAlert(`Tarea "${task}" ejecutada correctamente (${now})`, "success");

        // Actualizar timestamp
        const cellId = getTaskCellId(task);
        if (cellId) {
          $(`#${cellId}`).html(`<small class="text-success">${now}</small>`);
        }
      },
      error: function (xhr, status, error) {
        const msg = xhr.responseJSON?.message || `Error al ejecutar la tarea: ${error}`;
        showAlert(msg, "danger");
      },
      complete: function () {
        btn.html(originalText).prop("disabled", false);
      }
    });
  };

  // Función auxiliar
  function getTaskCellId(task) {
    switch (task) {
      case "cleanup": return "lastCleanupRun";
      case "mongo": return "lastMongoCheck";
      case "disk": return "lastDiskCheck";
      default: return "";
    }
  }

  // ============================================
  // EVENTOS DE BACKUP
  // ============================================
  function initializeBackupEvents() {
    console.log("✅ Inicializando eventos de backup...");

    $("#backupBtn")
      .off("click")
      .on("click", function () {
        console.log("✅ Click detectado en botón backup");
        const btn = $(this);
        const originalText = btn.html();

        btn
          .prop("disabled", true)
          .html(
            "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> Generando backup..."
          );

        $("#backupResult").html(`
          <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> Creando backup de la base de datos...
          </div>
        `);

        $.ajax({
          url: "/admin/maintenance/backup",
          method: "POST",
          xhrFields: { withCredentials: true },
          timeout: 60000,
          success: function (response) {
            if (response.status === "success" && response.uploaded_to_drive) {
              const successMsg = `
      <div class="alert alert-success">
        <i class="bi bi-check-circle"></i>
        <strong>Backup subido a Google Drive exitosamente</strong><br>
        <small>
          • Archivo: ${response.filename}<br>
          • Tamaño: ${(response.size / 1024).toFixed(2)} KB<br>
          • Documentos: ${response.total_documents}<br>
          • Colecciones: ${response.total_collections}<br>
          • Carpeta: ${response.drive_info.folder_name}<br>
          <a href="${response.drive_info.web_view_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
            <i class="bi bi-google"></i> Ver en Google Drive
          </a>
        </small>
      </div>
    `;
              $("#backupResult").html(successMsg);
              showAlert("Backup subido a Google Drive correctamente", "success");

              // Actualizar lista de backups de Google Drive si está visible
              if (typeof window.loadDriveBackups === "function") {
                setTimeout(() => window.loadDriveBackups(), 2000);
              }

              // Auto-cerrar el resultado después de 10 segundos
              setTimeout(() => {
                $("#backupResult").fadeOut(500, function () {
                  $(this).empty();
                });
              }, 10000);

            } else if (response.status === "warning" && !response.uploaded_to_drive) {
              const warningMsg = `
      <div class="alert alert-warning">
        <i class="bi bi-exclamation-triangle"></i>
        <strong>Backup creado con advertencias</strong><br>
        <small>
          ${response.message}<br>
          <a href="${response.download_url}" class="btn btn-sm btn-outline-primary mt-2">
            <i class="bi bi-download"></i> Descargar Backup Local
          </a>
        </small>
      </div>
    `;
              $("#backupResult").html(warningMsg);
              showAlert("Backup creado pero no subido a Google Drive", "warning");

              // Auto-cerrar el resultado después de 10 segundos
              setTimeout(() => {
                $("#backupResult").fadeOut(500, function () {
                  $(this).empty();
                });
              }, 10000);

            } else {
              $("#backupResult").html(`
      <div class="alert alert-warning">
        <i class="bi bi-exclamation-triangle"></i>
        Backup completado con advertencias
      </div>
    `);

              // Auto-cerrar el resultado después de 10 segundos
              setTimeout(() => {
                $("#backupResult").fadeOut(500, function () {
                  $(this).empty();
                });
              }, 10000);
            }
          },
          error: function (xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : xhr.statusText;
            $("#backupResult").html(`
              <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Error al crear backup</strong><br>
                <small>${errorMsg}</small>
              </div>
            `);
            showAlert("Error al generar backup: " + errorMsg, "danger");

            // Auto-cerrar el resultado después de 10 segundos
            setTimeout(() => {
              $("#backupResult").fadeOut(500, function () {
                $(this).empty();
              });
            }, 10000);
          },
          complete: function () {
            btn.prop("disabled", false).html(originalText);
          }
        });
      });
  }

  // ============================================
  // EVENTOS DE GOOGLE DRIVE
  // ============================================
  window.initializeGoogleDriveEvents = function () {
    console.log("✅ Inicializando eventos de Google Drive...");

    $("#restoreDriveModal").off("show.bs.modal").on("show.bs.modal", function () {
      console.log("🔵 [EVENT] show.bs.modal - Modal va a abrirse");
    });

    $("#restoreDriveModal").off("shown.bs.modal").on("shown.bs.modal", function () {
      console.log("✅ [EVENT] shown.bs.modal - Modal abierto exitosamente");
      // Solo cargar si no está ya cargando
      if (!isLoadingDriveBackups) {
        loadDriveBackups(true);
      }
    });

    // ✅ PRESERVADO: El botón principal sigue funcionando
    $("#restoreDriveBtn").off("click").on("click", function () {
      console.log("🔵 [EVENT] Botón Google Drive clickeado");
      // Solo cargar si no está ya cargando
      if (!isLoadingDriveBackups) {
        loadDriveBackups(true);
      }
    });

    // ✅ CORREGIDO: Solo cambio el selector del botón actualizar
    $("#refreshDriveBackups").off("click").on("click", function () {
      console.log("🔄 Actualizando lista de backups...");
      loadDriveBackups();
    });

    // Actualizar función de restauración con ventana emergente
    $(document).off("click", ".restore-drive-backup").on("click", ".restore-drive-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const fileId = $(this).data("id");
      const filename = $(this).data("filename");
      const btn = $(this);
      const originalText = btn.html();

      // Verificar si el botón ya está procesando
      if (btn.prop("disabled")) {
        return false;
      }

      if (!confirm(`¿Estás seguro de que quieres restaurar el backup "${filename}"?\n\nEsta acción sobrescribirá los datos actuales.`)) {
        return false;
      }

      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Restaurando...");

      $.ajax({
        url: `/admin/maintenance/drive/restore/${fileId}`,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ filename: filename }),
        xhrFields: { withCredentials: true },
        success: function (response) {
          if (response.status === "success" || response.success) {
            showConfirmationModal(
              "Restauración Completada",
              `El backup "${filename}" se ha restaurado correctamente. Los datos han sido actualizados.`,
              "success"
            );
          } else {
            showConfirmationModal(
              "Error en Restauración",
              `No se pudo restaurar el backup "${filename}". ${response.message || "Error desconocido"}.`,
              "error"
            );
          }
        },
        error: function (xhr) {
          showConfirmationModal(
            "Error en Restauración",
            `Error al restaurar el backup "${filename}": ${xhr.responseJSON?.message || xhr.statusText}`,
            "error"
          );
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });

      return false;
    });

    $(document).off("click", ".download-drive-backup").on("click", ".download-drive-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const filename = $(this).data("filename");
      const downloadUrl = $(this).data("download-url");
      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        return false;
      }

      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Descargando...");

      // Crear enlace temporal para descarga
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setTimeout(() => {
        btn.prop("disabled", false).html(originalText);
        showAlert(`Descarga iniciada: ${filename}`, "success");
      }, 1000);

      return false;
    });

    $(document).off("click", ".delete-drive-backup").on("click", ".delete-drive-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const fileId = $(this).data("id");
      const filename = $(this).data("filename");
      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        return false;
      }

      if (!confirm(`¿Estás seguro de que quieres eliminar el backup "${filename}"?\n\nEsta acción no se puede deshacer.`)) {
        return false;
      }

      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

      $.ajax({
        url: `/admin/maintenance/drive/delete/${fileId}`,
        method: "DELETE",
        xhrFields: { withCredentials: true },
        success: function (response) {
          if (response.status === "success" || response.success) {
            showAlert(`Backup "${filename}" eliminado correctamente`, "success");
            loadDriveBackups(); // Recargar lista
          } else {
            showAlert(`Error al eliminar backup: ${response.message || "Error desconocido"}`, "danger");
          }
        },
        error: function (xhr) {
          showAlert(`Error al eliminar backup: ${xhr.responseJSON?.message || xhr.statusText}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });

      return false;
    });

    // Eventos de paginación y controles
    $("#backupsPerPage").off("change").on("change", function () {
      backupsPerPage = parseInt($(this).val());
      currentPage = 1;
      displayBackupsWithPagination();
    });

    $("#selectAllBackups").off("change").on("change", function () {
      const isChecked = $(this).prop("checked");
      $(".backup-checkbox:not(:disabled)").prop("checked", isChecked);

      if (isChecked) {
        $(".backup-checkbox:not(:disabled)").each(function () {
          selectedBackups.add($(this).data("backup-id"));
        });
      } else {
        selectedBackups.clear();
      }

      updateDeleteButton();
    });

    $(document).off("change", ".backup-checkbox").on("change", ".backup-checkbox", function () {
      const backupId = $(this).data("backup-id");
      if ($(this).prop("checked")) {
        selectedBackups.add(backupId);
      } else {
        selectedBackups.delete(backupId);
      }
      updateDeleteButton();
    });

    $("#deleteSelectedBackups").off("click").on("click", function () {
      if (selectedBackups.size === 0) {
        showAlert("No hay backups seleccionados para eliminar", "warning");
        return;
      }

      if (!confirm(`¿Estás seguro de que quieres eliminar ${selectedBackups.size} backup(s)?\n\nEsta acción no se puede deshacer.`)) {
        return;
      }

      const btn = $(this);
      const originalText = btn.html();
      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

      const deletePromises = Array.from(selectedBackups).map(backupId =>
        $.ajax({
          url: `/admin/maintenance/drive/delete/${backupId}`,
          method: "DELETE",
          xhrFields: { withCredentials: true }
        })
      );

      Promise.all(deletePromises)
        .then(() => {
          showAlert(`${selectedBackups.size} backup(s) eliminado(s) correctamente`, "success");
          selectedBackups.clear();
          // Recargar lista inmediatamente con recarga forzada
          setTimeout(() => loadDriveBackups(true), 500);
        })
        .catch((error) => {
          showAlert("Error al eliminar algunos backups", "danger");
        })
        .finally(() => {
          btn.prop("disabled", false).html(originalText);
        });
    });
  };

  // Función para cargar backups de Google Drive
  window.loadDriveBackups = function (forceRefresh = false) {
    // Evitar llamadas duplicadas
    if (isLoadingDriveBackups) {
      console.log("⚠️ Carga de backups de Google Drive ya en progreso, saltando...");
      return;
    }

    console.log("🔄 Cargando backups de Google Drive...", forceRefresh ? "(forzando recarga)" : "");

    isLoadingDriveBackups = true;

    // Limpiar caché si se fuerza la recarga
    if (forceRefresh) {
      allBackups = [];
      console.log("🗑️ Caché de backups limpiada");
    }

    // Limpiar completamente el DOM
    $("#driveBackupsLoading").show();
    $("#driveBackupsContent").hide();
    $("#driveBackupsEmpty").hide();
    $("#driveBackupsError").hide();
    $("#driveBackupsTableBody").empty();

    // Limpiar selecciones
    selectedBackups.clear();
    updateDeleteButton();

    // Agregar timestamp para evitar caché del navegador
    const timestamp = new Date().getTime();
    const url = `/admin/maintenance/drive/backups?t=${timestamp}`;

    $.ajax({
      url: url,
      method: "GET",
      xhrFields: { withCredentials: true },
      cache: false, // Deshabilitar caché de jQuery
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      success: function (response) {
        console.log("📥 Respuesta de backups recibida:", response);
        $("#driveBackupsLoading").hide();

        if (response.success && response.backups && response.backups.length > 0) {
          // Actualizar caché con datos frescos
          allBackups = response.backups;
          displayDriveBackups(response.backups);
          $("#driveBackupsContent").show();
          // Reinicializar eventos después de cargar
          initializeDriveBackupsEvents();
        } else {
          // Limpiar caché si no hay backups
          allBackups = [];
          $("#driveBackupsEmpty").show();
          $("#driveBackupsCount").text("0 respaldos");
        }
      },
      error: function (xhr, status, error) {
        console.error("❌ Error cargando backups:", xhr.status, xhr.statusText, error);
        $("#driveBackupsLoading").hide();
        $("#driveBackupsError").show();
        $("#driveBackupsErrorMessage").text(`Error: ${xhr.statusText || "Error de conexión"}`);
        // Limpiar caché en caso de error
        allBackups = [];
      },
      complete: function () {
        isLoadingDriveBackups = false;
      }
    });
  };

  // Función para inicializar eventos de Google Drive
  function initializeDriveBackupsEvents() {
    console.log("🔧 Reinicializando eventos de Google Drive...");
    
    // Limpiar eventos existentes
    $(document).off("click", ".delete-drive-backup");
    $(document).off("click", ".download-drive-backup");
    $(document).off("click", ".restore-drive-backup");
    $(document).off("change", ".backup-checkbox");
    $(document).off("change", "#selectAllBackups");
    
    // Registrar eventos de eliminación individual
    $(document).on("click", ".delete-drive-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const fileId = $(this).data("id");
      const filename = $(this).data("filename");
      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        return false;
      }

      if (!confirm(`¿Estás seguro de que quieres eliminar el backup "${filename}"?\n\nEsta acción no se puede deshacer.`)) {
        return false;
      }

      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

      $.ajax({
        url: `/admin/maintenance/drive/delete/${fileId}`,
        method: "DELETE",
        xhrFields: { withCredentials: true },
        success: function (response) {
          if (response.status === "success" || response.success) {
            showAlert(`Backup "${filename}" eliminado correctamente`, "success");
            // Recargar lista inmediatamente con recarga forzada
            setTimeout(() => loadDriveBackups(true), 500);
          } else {
            showAlert(`Error al eliminar backup: ${response.message || "Error desconocido"}`, "danger");
          }
        },
        error: function (xhr) {
          showAlert(`Error al eliminar backup: ${xhr.responseJSON?.message || xhr.statusText}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });

      return false;
    });

    // Registrar eventos de checkbox
    $(document).on("change", ".backup-checkbox", function () {
      const backupId = $(this).data("backup-id");
      if ($(this).prop("checked")) {
        selectedBackups.add(backupId);
      } else {
        selectedBackups.delete(backupId);
      }
      updateDeleteButton();
    });

    $(document).on("change", "#selectAllBackups", function () {
      const isChecked = $(this).prop("checked");
      $(".backup-checkbox:not(:disabled)").prop("checked", isChecked);

      if (isChecked) {
        $(".backup-checkbox:not(:disabled)").each(function () {
          selectedBackups.add($(this).data("backup-id"));
        });
      } else {
        selectedBackups.clear();
      }

      updateDeleteButton();
    });
  }

  // Función para inicializar eventos individuales de backups locales
  function initializeLocalBackupsIndividualEvents() {
    console.log("🔧 Reinicializando eventos individuales de backups locales...");
    
    // Limpiar eventos existentes
    $(document).off("click", ".delete-local-backup");
    $(document).off("click", ".upload-local-backup");
    $(document).off("click", ".view-local-backup");
    
    // Registrar eventos de eliminación individual
    $(document).on("click", ".delete-local-backup", async function (e) {
      e.preventDefault();
      e.stopPropagation();
      const filename = $(this).data("filename");
      console.log("🗑️ Eliminando backup individual:", filename);

      const confirmed = await showConfirmDialog(
        "Confirmar Eliminación",
        `¿Estás seguro de que quieres eliminar el backup "${filename}"?\n\n⚠️ Esta acción no se puede deshacer.`,
        "danger"
      );

      if (!confirmed) {
        console.log("❌ Eliminación cancelada por el usuario");
        return;
      }

      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        console.log("⚠️ Botón ya deshabilitado, saltando...");
        return;
      }

      console.log("🚀 Iniciando eliminación de backup individual...");
      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

      $.ajax({
        url: `/admin/maintenance/local-backups/delete/${filename}`,
        method: "DELETE",
        xhrFields: { withCredentials: true },
        success: function (response) {
          console.log("✅ Respuesta de eliminación individual:", response);
                      if (response.success) {
              showModalAlert(`✅ ${response.message}`, "success");
              // Recargar lista inmediatamente con recarga forzada
              setTimeout(() => loadLocalBackups(true), 500);
            } else {
            showModalAlert(`❌ Error al eliminar: ${response.error}`, "danger");
          }
        },
        error: function (xhr) {
          console.error("❌ Error en eliminación individual:", xhr);
          const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
          showModalAlert(`❌ Error al eliminar backup: ${errorMsg}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });
    });

    // Registrar eventos de subida individual
    $(document).on("click", ".upload-local-backup", async function (e) {
      e.preventDefault();
      e.stopPropagation();
      const filename = $(this).data("filename");
      console.log("☁️ Subiendo backup individual:", filename);

      const confirmed = await showConfirmDialog(
        "Confirmar Subida",
        `¿Estás seguro de que quieres subir el backup "${filename}" a Google Drive?`,
        "warning"
      );

      if (!confirmed) {
        console.log("❌ Subida cancelada por el usuario");
        return;
      }

      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        console.log("⚠️ Botón ya deshabilitado, saltando...");
        return;
      }

      console.log("🚀 Iniciando subida de backup individual...");
      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Subiendo...");

      $.ajax({
        url: `/admin/maintenance/local-backups/upload-to-drive/${filename}`,
        method: "POST",
        xhrFields: { withCredentials: true },
        success: function (response) {
          console.log("✅ Respuesta de subida individual:", response);
          if (response.success) {
            showModalAlert(`✅ ${response.message}`, "success");
          } else {
            showModalAlert(`❌ Error al subir: ${response.error}`, "danger");
          }
        },
        error: function (xhr) {
          console.error("❌ Error en subida individual:", xhr);
          const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
          showModalAlert(`❌ Error al subir backup: ${errorMsg}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });
    });

    // Registrar eventos de vista previa
    $(document).on("click", ".view-local-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();
      const filename = $(this).data("filename");
      console.log("🔍 Vista previa de backup:", filename);
      showLocalBackupPreview(filename);
    });
  }

  // Función para mostrar backups de Google Drive
  function displayDriveBackups(backups) {
    // Destruir DataTable si existe
    if ($.fn.DataTable && $.fn.DataTable.isDataTable('#driveBackupsTable')) {
      $('#driveBackupsTable').DataTable().destroy();
    }
    
    // Limpiar completamente la tabla
    $("#driveBackupsTableBody").empty();

    backups.forEach(function (backup) {
      const sizeDisplay = backup.file_size ? `${(backup.file_size / (1024 * 1024)).toFixed(2)} MB` : "N/A";
      const uploadDate = backup.uploaded_at ? new Date(backup.uploaded_at).toLocaleString() : "N/A";
      const filename = backup.filename || "backup";
      const isSelected = selectedBackups.has(backup._id);
      const isPlaceholder = backup.is_placeholder || false;

      let actionButtons;
      if (isPlaceholder) {
        // Mostrar botones deshabilitados para placeholders
        actionButtons = `
          <div class="btn-group" role="group">
            <button class="btn btn-sm btn-secondary" disabled title="Google Drive no configurado">
              <i class="bi bi-gear"></i> Configurar
            </button>
            <small class="text-muted d-block mt-1">
              ${backup.error_message || "Configura las credenciales de Google Drive"}
            </small>
          </div>
        `;
      } else {
        // Generar URL de descarga directa de Google Drive
        const downloadUrl = `https://drive.google.com/uc?export=download&id=${backup._id}`;
        const viewUrl = `https://drive.google.com/file/d/${backup._id}/view`;

        actionButtons = `
          <div class="btn-group" role="group">
            <button class="btn btn-sm btn-primary download-drive-backup"
                    data-id="${backup._id}"
                    data-filename="${backup.filename}"
                    data-download-url="${downloadUrl}"
                    title="Descargar backup">
              <i class="bi bi-download"></i> Descargar
            </button>
            <button class="btn btn-sm btn-success restore-drive-backup"
                    data-id="${backup._id}"
                    data-filename="${backup.filename}"
                    title="Restaurar backup">
              <i class="bi bi-arrow-counterclockwise"></i> Restaurar
            </button>
            <button class="btn btn-sm btn-danger delete-drive-backup"
                    data-id="${backup._id}"
                    data-filename="${backup.filename}"
                    title="Eliminar backup">
              <i class="bi bi-trash"></i> Eliminar
            </button>
            <a href="${viewUrl}"
               class="btn btn-sm btn-info"
               target="_blank"
               title="Ver en Google Drive">
              <i class="bi bi-google"></i> Ver
            </a>
          </div>
        `;
      }

      const row = `
        <tr data-backup-id="${backup._id}" ${isPlaceholder ? "class=\"table-warning\"" : ""}>
          <td>
            <input type="checkbox" class="form-check-input backup-checkbox"
                   data-backup-id="${backup._id}" ${isSelected ? "checked" : ""}
                   ${isPlaceholder ? "disabled" : ""}>
          </td>
          <td>
            <i class="bi ${isPlaceholder ? "bi-exclamation-triangle text-warning" : "bi-file-earmark-zip text-primary"}"></i>
            ${filename}
          </td>
          <td>${sizeDisplay}</td>
          <td>${uploadDate}</td>
          <td>${backup.user || "N/A"}</td>
          <td>${actionButtons}</td>
        </tr>
      `;

      $("#driveBackupsTableBody").append(row);
    });

    $("#driveBackupsCount").text(`${backups.length} respaldo${backups.length !== 1 ? 's' : ''}`);

    // Inicializar DataTable para ordenamiento y paginación
    if ($.fn.DataTable) {
      if ($.fn.DataTable.isDataTable('#driveBackupsTable')) {
        $('#driveBackupsTable').DataTable().destroy();
      }

      $('#driveBackupsTable').DataTable({
        "order": [[3, "desc"]], // Ordenar por fecha descendente por defecto
        "pageLength": 25,
        "language": {
          "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        "columnDefs": [
          { "orderable": false, "targets": [0, 5] }, // Checkbox y acciones no ordenables
          { "type": "num", "targets": 2 } // Tamaño como número
        ]
      });
    }
  }



  // Función para actualizar botón de eliminar seleccionados
  function updateDeleteButton() {
    const selectedCount = selectedBackups.size;
    const btn = $("#deleteSelectedBackups");

    if (selectedCount > 0) {
      btn.prop("disabled", false).html(`<i class="bi bi-trash"></i> Eliminar ${selectedCount} seleccionado${selectedCount !== 1 ? 's' : ''}`);
    } else {
      btn.prop("disabled", true).html(`<i class="bi bi-trash"></i> Eliminar seleccionados`);
    }
  }



  // Botón de actualizar backups de Google Drive
  $("#refreshDriveBackups").off("click").on("click", function () {
    loadDriveBackups(true);
  });

  // Evento cuando se abre el modal de Google Drive
  $("#restoreDriveModal").off("shown.bs.modal").on("shown.bs.modal", function () {
    console.log("🔧 Modal de Google Drive abierto, inicializando...");
    // Forzar recarga completa del modal
    setTimeout(() => {
      if (!isLoadingDriveBackups) {
        loadDriveBackups(true);
      }
    }, 100);
  });

  // Inicializar botones de tareas
  function initializeTaskButtons() {
    console.log("🔧 Inicializando botones de tareas...");

    $(".run-task").each(function (index) {
      const btn = $(this);
      const task = btn.data("task");

      console.log(`🔧 Botón ${index + 1}: data-task="${task}"`);

      // Remover eventos existentes y agregar nuevo
      btn.off("click").on("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (task) {
          console.log(`🚀 Ejecutando tarea: ${task}`);
          window.runTask(task);
        }
      });
    });
  }

  // Inicializar otros eventos
  function initializeOtherEvents() {
    console.log("🔧 Inicializando otros eventos...");

    // Botón exportar CSV
    $("#exportSystemStatusBtn").off("click").on("click", function (e) {
      e.preventDefault();
      console.log("📊 Exportando estado del sistema...");

      const btn = $(this);
      const originalText = btn.html();

      btn.prop("disabled", true)
        .html("<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> Exportando...");

      $.ajax({
        url: "/admin/maintenance/export/csv",
        method: "POST",
        xhrFields: { withCredentials: true },
        success: function (response, status, xhr) {
          // Crear enlace temporal para descarga
          const blob = new Blob([response], { type: 'text/csv' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;

          // Obtener nombre del archivo del header Content-Disposition
          const contentDisposition = xhr.getResponseHeader('Content-Disposition');
          let filename = 'system_status.csv';
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
              filename = filenameMatch[1].replace(/['"]/g, '');
            }
          }

          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);

          showAlert("Archivo CSV exportado correctamente", "success");
        },
        error: function (xhr, status, error) {
          const errorMsg = xhr.responseJSON ? xhr.responseJSON.error : "Error al exportar CSV";
          showAlert(`Error al exportar CSV: ${errorMsg}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });
    });

    // Botón restaurar
    $("#restoreBtn").off("click").on("click", function (e) {
      e.preventDefault();
      $("#restoreFileInput").click();
    });

    // Manejo de archivo de restauración
    $("#restoreFileInput").off("change").on("change", function (e) {
      const file = e.target.files[0];
      if (!file) return;

      if (!file.name.toLowerCase().endsWith(".json") && !file.name.toLowerCase().endsWith(".gz")) {
        showAlert("Tipo de archivo inválido. Seleccione un archivo .json o .gz", "danger");
        return;
      }

      showAlert("Iniciando restauración desde archivo local...", "info");
    });

    // Modal de backups locales
    $("#localBackupsModal").off("show.bs.modal").on("show.bs.modal", function () {
      console.log("🔵 Modal de backups locales abriéndose");
      // Forzar recarga completa del modal
      setTimeout(() => {
        if (!isLoadingLocalBackups) {
          loadLocalBackups(true);
        }
      }, 100);
    });

    // Modal de opciones de backup
    $("#backupOptionsModal").off("show.bs.modal").on("show.bs.modal", function () {
      console.log("🔵 Modal de opciones de backup abriéndose");
    });

    // Modal de restauración local
    $("#restoreLocalModal").off("show.bs.modal").on("show.bs.modal", function () {
      console.log("🔵 Modal de restauración local abriéndose");
      // Forzar recarga completa del modal
      setTimeout(() => {
        if (!isLoadingLocalBackups) {
          loadRestoreLocalBackups(true);
        }
      }, 100);
    });

    // Botones de creación de backups
    $("#createLocalBackupBtn").off("click").on("click", function () {
      console.log("🔄 Botón crear backup local clickeado");
      createLocalBackup();
    });

    $("#createDriveBackupBtn").off("click").on("click", function () {
      console.log("🔄 Botón crear backup en Drive clickeado");
      createDriveBackup();
    });

    // Botón actualizar backups de restauración local
    $("#refreshRestoreLocalBackups").off("click").on("click", function () {
      console.log("🔄 Actualizando lista de backups de restauración local...");
      loadRestoreLocalBackups(true);
    });

    // Botón actualizar backups locales
    $("#refreshLocalBackups").off("click").on("click", function () {
      console.log("🔄 Actualizando lista de backups locales...");
      loadLocalBackups(true);
    });
  }

  // Función para cargar backups locales
  function loadLocalBackups(forceRefresh = false) {
    // Evitar llamadas duplicadas
    if (isLoadingLocalBackups) {
      console.log("⚠️ Carga de backups locales ya en progreso, saltando...");
      return;
    }

    console.log("🔄 Cargando backups locales...", forceRefresh ? "(forzando recarga)" : "");

    isLoadingLocalBackups = true;

    $("#localBackupsLoading").show();
    $("#localBackupsContent").hide();
    $("#localBackupsEmpty").hide();
    $("#localBackupsError").hide();
    $("#localBackupsTableBody").empty();

    // Limpiar selecciones
    $(".local-backup-checkbox").prop("checked", false);
    updateLocalBackupsSelectionUI();

    // Agregar timestamp para evitar caché del navegador
    const timestamp = new Date().getTime();
    const url = `/admin/maintenance/local-backups?t=${timestamp}`;

    $.ajax({
      url: url,
      method: "GET",
      xhrFields: { withCredentials: true },
      cache: false, // Deshabilitar caché de jQuery
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      success: function (response) {
        console.log("📥 Respuesta de backups locales recibida:", response);
        $("#localBackupsLoading").hide();

        if (response.success && response.backups && response.backups.length > 0) {
          displayLocalBackups(response.backups);
          $("#localBackupsContent").show();
          // Reinicializar acciones masivas después de mostrar los backups
          initializeLocalBackupsMassiveActions();
          // Reinicializar eventos individuales
          initializeLocalBackupsIndividualEvents();
        } else {
          $("#localBackupsEmpty").show();
          $("#localBackupsCount").text("0 backups");
        }
      },
      error: function (xhr, status, error) {
        console.error("❌ Error cargando backups locales:", xhr.status, xhr.statusText, error);
        $("#localBackupsLoading").hide();
        $("#localBackupsError").show();
        $("#localBackupsErrorMessage").text(`Error: ${xhr.statusText || "Error de conexión"}`);
      },
      complete: function () {
        isLoadingLocalBackups = false;
      }
    });
  }

  // Función para mostrar backups locales
  function displayLocalBackups(backups) {
    // Destruir DataTable si existe
    if ($.fn.DataTable && $.fn.DataTable.isDataTable('#localBackupsTable')) {
      $('#localBackupsTable').DataTable().destroy();
    }
    
    // Limpiar completamente la tabla
    $("#localBackupsTableBody").empty();

    backups.forEach(function (backup) {
      const sizeDisplay = backup.size_mb ? `${backup.size_mb} MB` : "N/A";
      const modifiedDate = backup.modified_at ? new Date(backup.modified_at).toLocaleString() : "N/A";

      const actionButtons = `
        <div class="btn-group" role="group">
          <button class="btn btn-sm btn-primary view-local-backup"
                  data-filename="${backup.filename}"
                  title="Ver detalles">
            <i class="bi bi-eye"></i> Ver
          </button>
          <button class="btn btn-sm btn-success upload-local-backup"
                  data-filename="${backup.filename}"
                  title="Subir a Google Drive">
            <i class="bi bi-cloud-upload"></i> Subir
          </button>
          <button class="btn btn-sm btn-danger delete-local-backup"
                  data-filename="${backup.filename}"
                  title="Eliminar backup">
            <i class="bi bi-trash"></i> Eliminar
          </button>
        </div>
      `;

      const row = `
        <tr data-backup-filename="${backup.filename}">
          <td>
            <input type="checkbox" class="form-check-input local-backup-checkbox" data-filename="${backup.filename}">
          </td>
          <td>
            <i class="bi bi-file-earmark-zip text-primary"></i>
            ${backup.filename}
          </td>
          <td>${sizeDisplay}</td>
          <td>${modifiedDate}</td>
          <td>${actionButtons}</td>
        </tr>
      `;

      $("#localBackupsTableBody").append(row);
    });

    $("#localBackupsCount").text(`${backups.length} backup${backups.length !== 1 ? 's' : ''}`);
    updateLocalBackupsSelectionUI();

    // Inicializar DataTable para ordenamiento
    if ($.fn.DataTable) {
      if ($.fn.DataTable.isDataTable('#localBackupsTable')) {
        $('#localBackupsTable').DataTable().destroy();
      }

      $('#localBackupsTable').DataTable({
        "order": [[3, "desc"]], // Ordenar por fecha descendente por defecto
        "pageLength": 25,
        "language": {
          "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        "columnDefs": [
          { "orderable": false, "targets": [0, 4] }, // Checkbox y acciones no ordenables
          { "type": "num", "targets": 2 } // Tamaño como número
        ]
      });
    }
  }

  // Función para actualizar UI de selección
  function updateLocalBackupsSelectionUI() {
    const totalCheckboxes = $(".local-backup-checkbox").length;
    const checkedCheckboxes = $(".local-backup-checkbox:checked").length;

    $("#selectedLocalBackupsCount").text(`${checkedCheckboxes} seleccionado${checkedCheckboxes !== 1 ? 's' : ''}`);

    // Habilitar/deshabilitar botones masivos
    $("#uploadSelectedLocalBackups, #deleteSelectedLocalBackups").prop("disabled", checkedCheckboxes === 0);

    // Actualizar checkbox "Seleccionar todos"
    const selectAllCheckbox = $("#selectAllLocalBackupsCheckbox");
    if (checkedCheckboxes === 0) {
      selectAllCheckbox.prop("indeterminate", false).prop("checked", false);
    } else if (checkedCheckboxes === totalCheckboxes) {
      selectAllCheckbox.prop("indeterminate", false).prop("checked", true);
    } else {
      selectAllCheckbox.prop("indeterminate", true);
    }
  }

  // Eventos para selección múltiple
  $(document).on("change", "#selectAllLocalBackupsCheckbox", function () {
    const isChecked = $(this).prop("checked");
    $(".local-backup-checkbox").prop("checked", isChecked);
    updateLocalBackupsSelectionUI();
  });

  $(document).on("change", ".local-backup-checkbox", function () {
    updateLocalBackupsSelectionUI();
  });

  // Botones de selección masiva
  $("#selectAllLocalBackups").on("click", function () {
    $(".local-backup-checkbox").prop("checked", true);
    updateLocalBackupsSelectionUI();
  });

  $("#deselectAllLocalBackups").on("click", function () {
    $(".local-backup-checkbox").prop("checked", false);
    updateLocalBackupsSelectionUI();
  });

  // Acciones masivas - Se registrarán cuando el modal se abra
  function initializeLocalBackupsMassiveActions() {
    console.log("🔧 Inicializando acciones masivas de backups locales...");

    // Verificar que los elementos existan antes de registrar eventos
    const uploadBtn = $("#uploadSelectedLocalBackups");
    const deleteBtn = $("#deleteSelectedLocalBackups");

    if (uploadBtn.length === 0) {
      console.warn("⚠️ Botón uploadSelectedLocalBackups no encontrado");
      return;
    }

    if (deleteBtn.length === 0) {
      console.warn("⚠️ Botón deleteSelectedLocalBackups no encontrado");
      return;
    }

    uploadBtn.off("click").on("click", async function () {
      console.log("☁️ Botón subir seleccionados clickeado");
      const selectedFiles = $(".local-backup-checkbox:checked").map(function () {
        return $(this).data("filename");
      }).get();

      if (selectedFiles.length === 0) {
        showAlert("No hay backups seleccionados", "warning");
        return;
      }

      const fileList = selectedFiles.join("\n• ");
      const confirmed = await showConfirmDialog(
        "Confirmar Subida Masiva",
        `¿Estás seguro de que quieres subir ${selectedFiles.length} backup${selectedFiles.length !== 1 ? 's' : ''} a Google Drive?\n\nArchivos seleccionados:\n• ${fileList}`,
        "warning"
      );

      if (!confirmed) {
        console.log("❌ Subida masiva cancelada por el usuario");
        return;
      }

      console.log("🚀 Iniciando subida masiva de backups...");
      uploadMultipleLocalBackups(selectedFiles);
    });

    deleteBtn.off("click").on("click", async function () {
      console.log("🗑️ Botón eliminar seleccionados clickeado");
      const selectedFiles = $(".local-backup-checkbox:checked").map(function () {
        return $(this).data("filename");
      }).get();

      if (selectedFiles.length === 0) {
        showAlert("No hay backups seleccionados", "warning");
        return;
      }

      const fileList = selectedFiles.join("\n• ");
      const confirmed = await showConfirmDialog(
        "Confirmar Eliminación Masiva",
        `¿Estás seguro de que quieres eliminar ${selectedFiles.length} backup${selectedFiles.length !== 1 ? 's' : ''}?\n\n⚠️ Esta acción no se puede deshacer.\n\nArchivos seleccionados:\n• ${fileList}`,
        "danger"
      );

      if (!confirmed) {
        console.log("❌ Eliminación masiva cancelada por el usuario");
        return;
      }

      console.log("🚀 Iniciando eliminación masiva de backups...");
      deleteMultipleLocalBackups(selectedFiles);
    });

    console.log("✅ Acciones masivas inicializadas correctamente");
  }

  // Función para subir múltiples backups
  function uploadMultipleLocalBackups(filenames) {
    const btn = $("#uploadSelectedLocalBackups");
    const originalText = btn.html();

    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Subiendo...");

    let completed = 0;
    let successCount = 0;
    let errorCount = 0;
    const errors = [];

    filenames.forEach(function (filename) {
      $.ajax({
        url: `/admin/maintenance/local-backups/upload-to-drive/${filename}`,
        method: "POST",
        xhrFields: { withCredentials: true },
        success: function (response) {
          if (response.success) {
            successCount++;
          } else {
            errorCount++;
            errors.push(`${filename}: ${response.error}`);
          }
        },
        error: function (xhr) {
          errorCount++;
          const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
          errors.push(`${filename}: ${errorMsg}`);
        },
        complete: function () {
          completed++;
          if (completed === filenames.length) {
            btn.prop("disabled", false).html(originalText);

            if (errorCount === 0) {
              showModalAlert(`✅ ${successCount} backup${successCount !== 1 ? 's' : ''} subido${successCount !== 1 ? 's' : ''} correctamente a Google Drive`, "success");
            } else {
              const errorMsg = errors.join("\n");
              showModalAlert(`⚠️ Subida completada con errores:\n\n${errorMsg}`, "warning");
            }
          }
        }
      });
    });
  }

  // Función para eliminar múltiples backups
  function deleteMultipleLocalBackups(filenames) {
    const btn = $("#deleteSelectedLocalBackups");
    const originalText = btn.html();

    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

    let completed = 0;
    let successCount = 0;
    let errorCount = 0;
    const errors = [];

    filenames.forEach(function (filename) {
      $.ajax({
        url: `/admin/maintenance/local-backups/delete/${filename}`,
        method: "DELETE",
        xhrFields: { withCredentials: true },
        success: function (response) {
          if (response.success) {
            successCount++;
          } else {
            errorCount++;
            errors.push(`${filename}: ${response.error}`);
          }
        },
        error: function (xhr) {
          errorCount++;
          const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
          errors.push(`${filename}: ${errorMsg}`);
        },
        complete: function () {
          completed++;
          if (completed === filenames.length) {
            btn.prop("disabled", false).html(originalText);

            if (errorCount === 0) {
              showModalAlert(`✅ ${successCount} backup${successCount !== 1 ? 's' : ''} eliminado${successCount !== 1 ? 's' : ''} correctamente`, "success");
              // Recargar lista inmediatamente con recarga forzada
              setTimeout(() => loadLocalBackups(true), 500);
            } else {
              const errorMsg = errors.join("\n");
              showModalAlert(`⚠️ Eliminación completada con errores:\n\n${errorMsg}`, "warning");
              // Recargar lista inmediatamente con recarga forzada
              setTimeout(() => loadLocalBackups(true), 500);
            }
          }
        }
      });
    });
  }

  // Eventos para acciones individuales de backups locales
  $(document).on("click", ".view-local-backup", function (e) {
    e.preventDefault();
    e.stopPropagation();
    const filename = $(this).data("filename");
    console.log("🔍 Vista previa de backup:", filename);
    showLocalBackupPreview(filename);
  });

  $(document).on("click", ".upload-local-backup", async function (e) {
    e.preventDefault();
    e.stopPropagation();
    const filename = $(this).data("filename");
    console.log("☁️ Subiendo backup individual:", filename);

    const confirmed = await showConfirmDialog(
      "Confirmar Subida",
      `¿Estás seguro de que quieres subir el backup "${filename}" a Google Drive?`,
      "warning"
    );

    if (!confirmed) {
      console.log("❌ Subida cancelada por el usuario");
      return;
    }

    const btn = $(this);
    const originalText = btn.html();

    if (btn.prop("disabled")) {
      console.log("⚠️ Botón ya deshabilitado, saltando...");
      return;
    }

    console.log("🚀 Iniciando subida de backup individual...");
    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Subiendo...");

    $.ajax({
      url: `/admin/maintenance/local-backups/upload-to-drive/${filename}`,
      method: "POST",
      xhrFields: { withCredentials: true },
      success: function (response) {
        console.log("✅ Respuesta de subida individual:", response);
        if (response.success) {
          showModalAlert(`✅ ${response.message}`, "success");
        } else {
          showModalAlert(`❌ Error al subir: ${response.error}`, "danger");
        }
      },
      error: function (xhr) {
        console.error("❌ Error en subida individual:", xhr);
        const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
        showModalAlert(`❌ Error al subir backup: ${errorMsg}`, "danger");
      },
      complete: function () {
        btn.prop("disabled", false).html(originalText);
      }
    });
  });

  $(document).on("click", ".delete-local-backup", async function (e) {
    e.preventDefault();
    e.stopPropagation();
    const filename = $(this).data("filename");
    console.log("🗑️ Eliminando backup individual:", filename);

    const confirmed = await showConfirmDialog(
      "Confirmar Eliminación",
      `¿Estás seguro de que quieres eliminar el backup "${filename}"?\n\n⚠️ Esta acción no se puede deshacer.`,
      "danger"
    );

    if (!confirmed) {
      console.log("❌ Eliminación cancelada por el usuario");
      return;
    }

    const btn = $(this);
    const originalText = btn.html();

    if (btn.prop("disabled")) {
      console.log("⚠️ Botón ya deshabilitado, saltando...");
      return;
    }

    console.log("🚀 Iniciando eliminación de backup individual...");
    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Eliminando...");

    $.ajax({
      url: `/admin/maintenance/local-backups/delete/${filename}`,
      method: "DELETE",
      xhrFields: { withCredentials: true },
      success: function (response) {
        console.log("✅ Respuesta de eliminación individual:", response);
        if (response.success) {
          showModalAlert(`✅ ${response.message}`, "success");
          loadLocalBackups(); // Recargar lista
        } else {
          showModalAlert(`❌ Error al eliminar: ${response.error}`, "danger");
        }
      },
      error: function (xhr) {
        console.error("❌ Error en eliminación individual:", xhr);
        const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
        showModalAlert(`❌ Error al eliminar backup: ${errorMsg}`, "danger");
      },
      complete: function () {
        btn.prop("disabled", false).html(originalText);
      }
    });
  });

  // Función para mostrar vista previa de backup
  function showLocalBackupPreview(filename) {
    // Por ahora, mostrar información básica
    const row = $(`tr[data-backup-filename="${filename}"]`);
    const size = row.find("td:eq(2)").text();
    const date = row.find("td:eq(3)").text();

    const previewContent = `
      <div class="alert alert-info">
        <h6><i class="bi bi-file-earmark-zip"></i> ${filename}</h6>
        <p><strong>Tamaño:</strong> ${size}</p>
        <p><strong>Fecha de modificación:</strong> ${date}</p>
        <p><strong>Ubicación:</strong> Directorio local de backups</p>
        <hr>
        <p class="mb-0"><small>La vista previa completa del contenido del backup estará disponible en futuras versiones.</small></p>
      </div>
    `;

    // Crear modal temporal para la vista previa
    const modal = $(`
      <div class="modal fade" id="backupPreviewModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-eye"></i> Vista Previa: ${filename}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              ${previewContent}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
          </div>
        </div>
      </div>
    `);

    // Remover modal anterior si existe
    $("#backupPreviewModal").remove();

    // Agregar y mostrar el nuevo modal
    $("body").append(modal);
    const bsModal = new bootstrap.Modal(document.getElementById('backupPreviewModal'));
    bsModal.show();

    // Limpiar modal al cerrar
    $("#backupPreviewModal").off("hidden.bs.modal").on("hidden.bs.modal", function () {
      $(this).remove();
    });
  }

  // Función para cargar estado del sistema
  function loadSystemStatus() {
    $.ajax({
      url: "/admin/api/system_status",
      method: "GET",
      success: function (data) {
        if (data.system_status) {
          const system = data.system_status;

          // Actualizar memoria
          if (system.memory_usage) {
            const mem = system.memory_usage;
            $("#memoriaUsage").css("width", `${mem.percent || 0}%`).text(`${mem.percent || 0}%`);
            $("#memTotal").text(mem.total_gb || (mem.total_mb / 1024).toFixed(2));
            $("#memDisponible").text(mem.available_gb || (mem.available_mb / 1024).toFixed(2));
          }

          // Actualizar CPU
          if (system.cpu_usage !== undefined) {
            $("#cpuUsage").css("width", `${system.cpu_usage}%`).text(`${system.cpu_usage}%`);
          }

          // Actualizar detalles del sistema
          if (system.system_details) {
            const details = system.system_details;
            $("#so").text(details.os || "N/A");
            $("#arquitectura").text(details.arch || "N/A");
            $("#usuario").text(details.user || "N/A");
            $("#hora").text(new Date().toLocaleString());
          }
        }
      },
      error: function () {
        console.error("Error al cargar estado del sistema");
      }
    });
  }

  // Función para cargar backups de restauración local
  function loadRestoreLocalBackups(forceRefresh = false) {
    // Evitar llamadas duplicadas
    if (isLoadingLocalBackups) {
      console.log("⚠️ Carga de backups de restauración local ya en progreso, saltando...");
      return;
    }

    console.log("🔄 Cargando backups de restauración local...", forceRefresh ? "(forzando recarga)" : "");

    isLoadingLocalBackups = true;

    $("#restoreLocalBackupsLoading").show();
    $("#restoreLocalBackupsContent").hide();
    $("#restoreLocalBackupsEmpty").hide();
    $("#restoreLocalBackupsError").hide();
    $("#restoreLocalBackupsTableBody").empty();

    // Agregar timestamp para evitar caché del navegador
    const timestamp = new Date().getTime();
    const url = `/admin/maintenance/local-backups?t=${timestamp}`;

    $.ajax({
      url: url,
      method: "GET",
      xhrFields: { withCredentials: true },
      cache: false, // Deshabilitar caché de jQuery
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      },
      success: function (response) {
        console.log("📥 Respuesta de backups de restauración local recibida:", response);
        $("#restoreLocalBackupsLoading").hide();

        if (response.success && response.backups && response.backups.length > 0) {
          displayRestoreLocalBackups(response.backups);
          $("#restoreLocalBackupsContent").show();
          // Reinicializar eventos después de cargar
          initializeRestoreLocalBackupsEvents();
        } else {
          $("#restoreLocalBackupsEmpty").show();
          $("#restoreLocalBackupsCount").text("0 backups");
        }
      },
      error: function (xhr, status, error) {
        console.error("❌ Error cargando backups de restauración local:", xhr.status, xhr.statusText, error);
        $("#restoreLocalBackupsLoading").hide();
        $("#restoreLocalBackupsError").show();
        $("#restoreLocalBackupsErrorMessage").text(`Error: ${xhr.statusText || "Error de conexión"}`);
      },
      complete: function () {
        isLoadingLocalBackups = false;
      }
    });
  }

  // Función para mostrar backups de restauración local
  function displayRestoreLocalBackups(backups) {
    // Destruir DataTable si existe
    if ($.fn.DataTable && $.fn.DataTable.isDataTable('#restoreLocalBackupsTable')) {
      $('#restoreLocalBackupsTable').DataTable().destroy();
    }
    
    // Limpiar completamente la tabla
    $("#restoreLocalBackupsTableBody").empty();

    backups.forEach(function (backup) {
      const sizeDisplay = backup.size_mb ? `${backup.size_mb} MB` : "N/A";
      const modifiedDate = backup.modified_at ? new Date(backup.modified_at).toLocaleString() : "N/A";

      const actionButtons = `
        <div class="btn-group" role="group">
          <button class="btn btn-sm btn-warning restore-local-backup"
                  data-filename="${backup.filename}"
                  title="Restaurar backup">
            <i class="bi bi-arrow-counterclockwise"></i> Restaurar
          </button>
          <button class="btn btn-sm btn-info view-restore-local-backup"
                  data-filename="${backup.filename}"
                  title="Ver detalles">
            <i class="bi bi-eye"></i> Ver
          </button>
        </div>
      `;

      const row = `
        <tr data-backup-filename="${backup.filename}">
          <td>
            <i class="bi bi-file-earmark-zip text-warning"></i>
            ${backup.filename}
          </td>
          <td>${sizeDisplay}</td>
          <td>${modifiedDate}</td>
          <td>${actionButtons}</td>
        </tr>
      `;

      $("#restoreLocalBackupsTableBody").append(row);
    });

    $("#restoreLocalBackupsCount").text(`${backups.length} backup${backups.length !== 1 ? 's' : ''}`);

    // Inicializar DataTable para ordenamiento
    if ($.fn.DataTable) {
      $('#restoreLocalBackupsTable').DataTable({
        "order": [[2, "desc"]], // Ordenar por fecha descendente por defecto
        "pageLength": 25,
        "language": {
          "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        "columnDefs": [
          { "orderable": false, "targets": [3] }, // Acciones no ordenables
          { "type": "num", "targets": 1 } // Tamaño como número
        ]
      });
    }
  }

  // Función para inicializar eventos de restauración local
  function initializeRestoreLocalBackupsEvents() {
    console.log("🔧 Reinicializando eventos de restauración local...");
    
    // Limpiar eventos existentes
    $(document).off("click", ".restore-local-backup");
    $(document).off("click", ".view-restore-local-backup");
    
    // Registrar eventos de restauración
    $(document).on("click", ".restore-local-backup", async function (e) {
      e.preventDefault();
      e.stopPropagation();
      const filename = $(this).data("filename");
      console.log("🔄 Restaurando backup local:", filename);

      const confirmed = await showConfirmDialog(
        "Confirmar Restauración",
        `¿Estás seguro de que quieres restaurar el backup "${filename}"?\n\n⚠️ Esta acción sobrescribirá todos los datos actuales y no se puede deshacer.\n\nAsegúrate de tener un backup reciente antes de continuar.`,
        "danger"
      );

      if (!confirmed) {
        console.log("❌ Restauración cancelada por el usuario");
        return;
      }

      const btn = $(this);
      const originalText = btn.html();

      if (btn.prop("disabled")) {
        console.log("⚠️ Botón ya deshabilitado, saltando...");
        return;
      }

      console.log("🚀 Iniciando restauración de backup local...");
      btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Restaurando...");

      $.ajax({
        url: `/admin/maintenance/local-backups/restore/${filename}`,
        method: "POST",
        xhrFields: { withCredentials: true },
        success: function (response) {
          console.log("✅ Respuesta de restauración local:", response);
          if (response.success) {
            showModalAlert(`✅ ${response.message}`, "success");
            // Cerrar modal después de restauración exitosa
            setTimeout(() => {
              $('#restoreLocalModal').modal('hide');
            }, 2000);
          } else {
            showModalAlert(`❌ Error al restaurar: ${response.error}`, "danger");
          }
        },
        error: function (xhr) {
          console.error("❌ Error en restauración local:", xhr);
          const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
          showModalAlert(`❌ Error al restaurar backup: ${errorMsg}`, "danger");
        },
        complete: function () {
          btn.prop("disabled", false).html(originalText);
        }
      });
    });

    // Registrar eventos de vista previa
    $(document).on("click", ".view-restore-local-backup", function (e) {
      e.preventDefault();
      e.stopPropagation();
      const filename = $(this).data("filename");
      console.log("🔍 Vista previa de backup de restauración:", filename);
      showLocalBackupPreview(filename);
    });
  }

  // Función para crear backup local
  function createLocalBackup() {
    console.log("🔄 Creando backup local...");
    
    const btn = $("#createLocalBackupBtn");
    const originalText = btn.html();
    
    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Creando...");

    $.ajax({
      url: "/admin/maintenance/backup/local",
      method: "POST",
      xhrFields: { withCredentials: true },
      success: function (response) {
        console.log("✅ Respuesta de creación de backup local:", response);
        if (response.success) {
          showAlert(`✅ ${response.message}`, "success");
          // Cerrar modal de opciones
          $('#backupOptionsModal').modal('hide');
        } else {
          showAlert(`❌ Error al crear backup: ${response.error}`, "danger");
        }
      },
      error: function (xhr) {
        console.error("❌ Error creando backup local:", xhr);
        const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
        showAlert(`❌ Error al crear backup local: ${errorMsg}`, "danger");
      },
      complete: function () {
        btn.prop("disabled", false).html(originalText);
      }
    });
  }

  // Función para crear backup en Google Drive
  function createDriveBackup() {
    console.log("🔄 Creando backup en Google Drive...");
    
    const btn = $("#createDriveBackupBtn");
    const originalText = btn.html();
    
    btn.prop("disabled", true).html("<span class=\"spinner-border spinner-border-sm\"></span> Creando...");

    $.ajax({
      url: "/admin/maintenance/backup/drive",
      method: "POST",
      xhrFields: { withCredentials: true },
      success: function (response) {
        console.log("✅ Respuesta de creación de backup en Drive:", response);
        if (response.success) {
          showAlert(`✅ ${response.message}`, "success");
          // Cerrar modal de opciones
          $('#backupOptionsModal').modal('hide');
        } else {
          showAlert(`❌ Error al crear backup: ${response.error}`, "danger");
        }
      },
      error: function (xhr) {
        console.error("❌ Error creando backup en Drive:", xhr);
        const errorMsg = xhr.responseJSON?.error || xhr.statusText || "Error desconocido";
        showAlert(`❌ Error al crear backup en Google Drive: ${errorMsg}`, "danger");
      },
      complete: function () {
        btn.prop("disabled", false).html(originalText);
      }
    });
  }

  // Inicialización principal
  function initializeDashboard() {
    console.log("🔧 Inicializando dashboard completo...");

    // Inicializar todos los eventos
    initializeTaskButtons();
    initializeOtherEvents();
    initializeBackupEvents();
    window.initializeGoogleDriveEvents();

    // Inicializar eventos de Google Drive y locales
    initializeDriveBackupsEvents();
    initializeLocalBackupsIndividualEvents();

    // Cargar estado del sistema
    loadSystemStatus();

    // Actualizar estado del sistema cada 30 segundos
    setInterval(loadSystemStatus, 30000);

    // Eliminar duplicados cada 2 segundos como medida de seguridad
    setInterval(removeDuplicateAlerts, 2000);

    console.log("✅ Dashboard inicializado correctamente");
  }

  // Esperar a que los elementos estén disponibles
  function waitForElements() {
    const maxAttempts = 20;
    let attempts = 0;

    function checkElements() {
      attempts++;
              // console.log(`🔍 Verificando elementos (${attempts}/${maxAttempts})...`);

      const runTaskButtons = $(".run-task");
      const backupBtn = $("#backupBtn");
      const exportBtn = $("#exportSystemStatusBtn");

      if (runTaskButtons.length > 0 || backupBtn.length > 0 || exportBtn.length > 0) {
        console.log("✅ Elementos encontrados, inicializando...");
        initializeDashboard();
        return;
      }

      if (attempts >= maxAttempts) {
        console.warn("⚠️ Timeout alcanzado, inicializando con elementos disponibles...");
        initializeDashboard();
        return;
      }

      setTimeout(checkElements, 500);
    }

    checkElements();
  }

  // Iniciar verificación de elementos
  waitForElements();
});