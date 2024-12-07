       var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        })

        document.addEventListener('DOMContentLoaded', function() {
            var hash = window.location.hash;
            if (hash) {
                var tab = new bootstrap.Tab(document.querySelector('a[href="' + hash + '"]'));
                tab.show();
            }
        });

        var tabLinks = document.querySelectorAll('a[data-bs-toggle="tab"]');
        tabLinks.forEach(function(tabLink) {
            tabLink.addEventListener('shown.bs.tab', function (e) {
                window.location.hash = e.target.getAttribute('href');
            });
        });

        document.addEventListener("DOMContentLoaded", () => {
  const modal = new bootstrap.Modal(document.getElementById("deleteCategoryModal"));
  const deleteButtons = document.querySelectorAll(".delete-category-button");
  const deleteForm = document.getElementById("deleteCategoryForm");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const actionUrl = this.getAttribute("data-url");
      deleteForm.action = actionUrl; // Asigna la URL al formulario
      modal.show();
    });
  });
});

  document.addEventListener("DOMContentLoaded", () => {
  const accountModal = new bootstrap.Modal(document.getElementById("deleteAccountModal"));
  const deleteAccountButtons = document.querySelectorAll(".delete-account-button");
  const deleteAccountForm = document.getElementById("deleteAccountForm");

  deleteAccountButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const actionUrl = this.getAttribute("data-url");
      deleteAccountForm.action = actionUrl;
      accountModal.show();
    });
  });
});

$(document).ready(function() {
  $('#messageModal').modal('show');
  setTimeout(function() {
      $('#messageModal').modal('hide');
  }, 2000);
});