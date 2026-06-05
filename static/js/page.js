document.addEventListener('DOMContentLoaded', function() {
    try {
        fetch('/employee_list')
            .then(response => response.text())
            .then(html => {
                document.getElementById('emplist').innerHTML = html;
                attachRowClickEvents();
            });

        function attachRowClickEvents() {
            const tableRows = document.querySelectorAll("#emplist tbody tr");
            for (const tableRow of tableRows) {
                tableRow.addEventListener("click", function () {
                    performOperation('details_dialog', parseInt(tableRow.id));
                });
            }
        }

    } catch (error) {
        console.error('Erreur:', error);
    }
});

async function performOperation(action, arg = 0, isHtmx = false) {
    try {
        var url = `/${action}`;
        const headers = {
            'Content-Type': 'application/json',
        };
        if (isHtmx) {
            headers['HX-Request'] = 'true';
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({id: arg}),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const html = await response.text();
        if (action == "employee_list") {
            document.getElementById('emplist').innerHTML = html;
            attachRowClickEvents();
        } else if (action == "details_dialog") {
            document.getElementById('emp_detail').innerHTML = html;
            document.getElementById('employeeModal').style.display = 'block';
            //document.getElementById('operationsModal').style.visibility = 'hidden';
        } else {
            document.getElementById('dialog').innerHTML = html;
            document.getElementById('operationsModal').style.display = 'block';
            document.getElementById('operationsModal').style.visibility = 'visible';
        }
        if (action == "hierarchy_dialog" || action == "subalterns_dialog") {
            showTree()
        }
        if (action == "entholidays_dialog" ||
            action == "holidays_dialog" ||
            action == "add_new_entholidays_dialog" ||
            action == "delete_entholidays_dialog" ||
            action == "update_entholidays_dialog") {
            filter_holidays();
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

function showTree() {
    var toggler = document.getElementsByClassName("caret");
    var i;

    for (i = 0; i < toggler.length; i++) {
      toggler[i].addEventListener("click", function() {
        this.parentElement.querySelector(".nested").classList.toggle("active");
        this.classList.toggle("caret-down");
      });
    }
}

// filter the rows of the employee's list table
function filterData() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("emplist");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td0 = tr[i].getElementsByTagName("td")[0];
        td1 = tr[i].getElementsByTagName("td")[1];
        if (td0 || td1) {
            txtValue = (td0.textContent + " " + td1.textContent); //|| td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function closeOpModal() {
    document.getElementById('operationsModal').style.display = 'none';
}

let sortDirections = {};

function sortTable(columnIndex) {
  const table = document.getElementById("employee_table");
  const tbody = table.tBodies[0];
  // Convertit la collection HTML des lignes (tr) en un véritable tableau JS
  const rows = Array.from(tbody.rows);

  // Alterne la direction : si déjà 'asc', passe à 'desc', sinon reste à 'asc'
  const currentDirection = sortDirections[columnIndex] === 'asc' ? 'desc' : 'asc';
  sortDirections = { [columnIndex]: currentDirection };

  // Trie les lignes en comparant le texte des cellules de la colonne sélectionnée
  rows.sort((rowA, rowB) => {
    const cellA = rowA.cells[columnIndex].textContent.trim();
    const cellB = rowB.cells[columnIndex].textContent.trim();

    // Vérifie si les valeurs sont numériques pour appliquer un tri de nombres
    const isNum = !isNaN(cellA) && !isNaN(cellB);

    if (isNum) {
      return currentDirection === 'asc' ? cellA - cellB : cellB - cellA;
    } else {
      return currentDirection === 'asc'
        ? cellA.localeCompare(cellB)
        : cellB.localeCompare(cellA);
    }
  });

  // Réinsère les lignes triées dans le tbody (replaceChildren vide puis ajoute l'array)
  tbody.replaceChildren(...rows);
}
