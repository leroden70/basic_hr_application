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

async function performOperation(action, arg = 0) {
    try {
        var url = `/${action}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: arg }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const html = await response.text();
        if (action == "details_dialog") {
            document.getElementById('emp_detail').innerHTML = html;
            document.getElementById('employeeModal').style.display = 'block';
            document.getElementById('operationsModal').style.visibility = 'hidden';
        } else {
            document.getElementById('dialog').innerHTML = html;
            document.getElementById('operationsModal').style.display = 'block';
            document.getElementById('operationsModal').style.visibility = 'visible';
        }
        if (action == "hierarchy_dialog" || action == "subalterns_dialog") {
            showTree()
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
