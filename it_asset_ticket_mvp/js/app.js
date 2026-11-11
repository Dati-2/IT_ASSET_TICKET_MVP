const STORAGE_KEY = "itDeskMvpData";
const API_BASE = "http://127.0.0.1:5000/api";
async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, options);

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return response.json();
}

async function loadUsersFromAPI() {
    try {
        const users = await apiRequest("/users");

        data.users = users.map(user => ({
            id: user.id,
            staffCode: user.staff_code,
            name: user.name,
            email: user.email,
            department: user.department,
            role: user.role
        }));

        renderUsers();

    } catch (error) {
        console.error("Error loading users:", error);
        showToast("Could not load users from the server");
    }
}

async function loadAssetsFromAPI() {
    try {
        const assets = await apiRequest("/assets");

        data.assets = assets.map(asset => ({
            id: asset.id,
            name: asset.name,
            tag: asset.tag,
            serial: asset.serial,
            category: asset.category,
            assignedTo: asset.assigned_to,
            status: asset.status
        }));

        renderAssets();

    } catch (error) {
        console.error("Error loading assets:", error);
        showToast("Could not load assets from the server");
    }
}

async function loadTicketsFromAPI() {
    try {
        const tickets = await apiRequest("/tickets");

        data.tickets = tickets.map(ticket => ({
            id: ticket.id,
            title: ticket.title,
            description: ticket.description,
            reportedBy: ticket.reported_by,
            priority: ticket.priority,
            status: ticket.status,
            date: ticket.date_raised
        }));

        renderTickets();

    } catch (error) {
        console.error("Error loading tickets:", error);
        showToast("Could not load tickets from the server");
    }
}

const seedData = {
  users: [
    {id:1,name:"Ada Okafor",email:"ada.okafor@example.com",department:"Finance",role:"Employee"},
    {id:2,name:"Daniel James",email:"daniel.james@example.com",department:"Operations",role:"Employee"},
    {id:3,name:"Mary Johnson",email:"mary.johnson@example.com",department:"IT",role:"IT Support"},
    {id:4,name:"Samuel Peter",email:"samuel.peter@example.com",department:"Human Resources",role:"Employee"}
  ],
  assets: [
    {id:1,name:"HP ProBook 450",tag:"AST-001",serial:"HP450-2024-001",category:"Laptop",assignedTo:1,status:"Assigned"},
    {id:2,name:"Dell 24-inch Monitor",tag:"AST-002",serial:"DELL24-8821",category:"Monitor",assignedTo:2,status:"Assigned"},
    {id:3,name:"Logitech Wireless Mouse",tag:"AST-003",serial:"LOG-M185-431",category:"Accessory",assignedTo:null,status:"Available"},
    {id:4,name:"Lenovo ThinkPad E14",tag:"AST-004",serial:"LEN-E14-9912",category:"Laptop",assignedTo:null,status:"Maintenance"}
  ],
  tickets: [
    {id:1001,title:"Laptop not connecting to Wi-Fi",description:"Unable to connect to the office wireless network.",reportedBy:1,priority:"High",status:"Open",date:"2026-11-09"},
    {id:1002,title:"Printer not responding",description:"The Finance department printer is not responding.",reportedBy:2,priority:"Medium",status:"In Progress",date:"2026-11-09"},
    {id:1003,title:"Email password reset",description:"User requires assistance resetting email password.",reportedBy:4,priority:"Low",status:"Resolved",date:"2026-11-08"}
  ]
};
let data = loadData();
let editing = null;
let currentFormType = null;

function loadData(){try{return JSON.parse(localStorage.getItem(STORAGE_KEY)) || structuredClone(seedData)}catch{return structuredClone(seedData)}}
function saveData(){localStorage.setItem(STORAGE_KEY,JSON.stringify(data))}
function nextId(list){return list.length ? Math.max(...list.map(x=>Number(x.id)))+1 : 1}
function escapeHTML(value=""){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function userName(id){return data.users.find(u=>u.id===Number(id))?.name || "Unassigned"}
function statusClass(status){return ({Available:"available",Assigned:"assigned",Maintenance:"maintenance",Open:"open","In Progress":"progress",Resolved:"resolved"})[status]||"low"}
function badge(status){return `<span class="badge badge-${statusClass(status)}">${escapeHTML(status)}</span>`}
function showToast(message){const el=document.getElementById("toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2400)}
function showPage(page){
  document.querySelectorAll(".page-view").forEach(v=>v.classList.toggle("active",v.id===`page-${page}`));
  document.querySelectorAll(".nav-item").forEach(v=>v.classList.toggle("active",v.dataset.page===page));
  document.getElementById("pageCrumb").textContent=({dashboard:"Dashboard",assets:"IT Assets",tickets:"Tickets",users:"Users"})[page];
  document.getElementById("sidebar").classList.remove("open");
  renderAll();
}
function renderDashboard(){
  const available=data.assets.filter(a=>a.status==="Available").length;
  const assigned=data.assets.filter(a=>a.status==="Assigned").length;
  const maintenance=data.assets.filter(a=>a.status==="Maintenance").length;
  const open=data.tickets.filter(t=>t.status!=="Resolved").length;
  document.getElementById("statAssets").textContent=data.assets.length;
  document.getElementById("statAvailable").textContent=available;
  document.getElementById("statAssigned").textContent=assigned;
  document.getElementById("statOpen").textContent=open;
  document.getElementById("summaryAvailable").textContent=available;
  document.getElementById("summaryAssigned").textContent=assigned;
  document.getElementById("summaryMaintenance").textContent=maintenance;
  const total=data.assets.length||1;
  document.getElementById("assetBarAvailable").style.width=`${available/total*100}%`;
  document.getElementById("assetBarAssigned").style.width=`${assigned/total*100}%`;
  document.getElementById("assetBarMaintenance").style.width=`${maintenance/total*100}%`;
  document.getElementById("assetSummaryFoot").textContent=`${data.assets.length} asset${data.assets.length===1?"":"s"} registered in the system.`;
  const rows=[...data.tickets].sort((a,b)=>b.id-a.id).slice(0,4);
  document.getElementById("recentTickets").innerHTML=rows.length?rows.map(t=>`<tr><td><strong>#${t.id}</strong></td><td>${escapeHTML(t.title)}</td><td>${badge(t.priority)}</td><td>${badge(t.status)}</td></tr>`).join(""):`<tr><td colspan="4">No tickets have been created.</td></tr>`;
}
function renderAssets(){
  const q=(document.getElementById("assetSearch")?.value||"").toLowerCase();
  const f=document.getElementById("assetFilter")?.value||"";
  const rows=data.assets.filter(a=>(`${a.name} ${a.tag} ${a.serial} ${a.category}`.toLowerCase().includes(q))&&(!f||a.status===f));
  document.getElementById("assetsTable").innerHTML=rows.map(a=>`<tr><td><strong>${escapeHTML(a.name)}</strong><br><small>${escapeHTML(a.serial)}</small></td><td>${escapeHTML(a.tag)}</td><td>${escapeHTML(a.category)}</td><td>${escapeHTML(userName(a.assignedTo))}</td><td>${badge(a.status)}</td><td><div class="action-group"><button class="table-action" data-edit="asset" data-id="${a.id}">Edit</button><button class="table-action" data-delete="asset" data-id="${a.id}">Delete</button></div></td></tr>`).join("");
  document.getElementById("assetsEmpty").classList.toggle("hidden",rows.length>0);
}
function renderTickets(){
  const q=(document.getElementById("ticketSearch")?.value||"").toLowerCase();
  const f=document.getElementById("ticketFilter")?.value||"";
  const rows=[...data.tickets].sort((a,b)=>b.id-a.id).filter(t=>(`${t.id} ${t.title} ${userName(t.reportedBy)}`.toLowerCase().includes(q))&&(!f||t.status===f));
  document.getElementById("ticketsTable").innerHTML=rows.map(t=>`<tr><td><strong>#${t.id}</strong></td><td><strong>${escapeHTML(t.title)}</strong><br><small>${escapeHTML(t.description).slice(0,55)}</small></td><td>${escapeHTML(userName(t.reportedBy))}</td><td>${badge(t.priority)}</td><td>${escapeHTML(t.date)}</td><td>${badge(t.status)}</td><td><div class="action-group"><button class="table-action" data-edit="ticket" data-id="${t.id}">Update</button><button class="table-action" data-delete="ticket" data-id="${t.id}">Delete</button></div></td></tr>`).join("");
  document.getElementById("ticketsEmpty").classList.toggle("hidden",rows.length>0);
}
function renderUsers(){
  const q = (document.getElementById("userSearch")?.value || "")
    .trim()
    .toLowerCase();

  const rows = data.users.filter(u => {
    const searchableText =
      `${u.id} ${u.name} ${u.email} ${u.department} ${u.role}`.toLowerCase();

    return searchableText.includes(q);
  });

  document.getElementById("usersTable").innerHTML = rows.map(u => `
    <tr>
      <td><div class="user-cell"><strong>${escapeHTML(u.name)}</strong></div></td>
      <td>${escapeHTML(u.email)}</td>
      <td>${escapeHTML(u.department)}</td>
      <td>${escapeHTML(u.role)}</td>
      <td>${data.assets.filter(a => a.assignedTo === u.id).length}</td>
      <td>
        <div class="action-group">
          <button class="table-action" data-edit="user" data-id="${u.id}">Edit</button>
          <button class="table-action" data-delete="user" data-id="${u.id}">Delete</button>
        </div>
      </td>
    </tr>
  `).join("");

  const emptyMessage = document.getElementById("usersEmpty");
  emptyMessage.textContent = q
    ? "No matching users found."
    : "No users found. Add your first employee.";

  emptyMessage.classList.toggle("hidden", rows.length > 0);
}
function renderAll(){renderDashboard();renderAssets();renderTickets();renderUsers()}

function field(label,name,type="text",value="",options=null,full=false,required=true){
  let control="";
  if(type==="select")control=`<select name="${name}" ${required?"required":""}>${options.map(o=>`<option value="${escapeHTML(o.value)}" ${String(o.value)===String(value)?"selected":""}>${escapeHTML(o.label)}</option>`).join("")}</select>`;
  else if(type==="textarea")control=`<textarea name="${name}" ${required?"required":""}>${escapeHTML(value)}</textarea>`;
  else control=`<input type="${type}" name="${name}" value="${escapeHTML(value)}" ${required?"required":""}>`;
  return `<div class="field ${full?"full":""}"><label>${label}</label>${control}</div>`;
}
function openForm(type,id=null){
  currentFormType=type;editing=id;
  const record=id?data[`${type}s`].find(x=>x.id===Number(id)):null;
  const fields=document.getElementById("formFields");
  let html="";

 if (type === "asset") {
    const userOptions = data.users.map(u => ({
        value: u.id,
        label: `${u.name} (${u.staffCode || ""})`
    }));

    const selectedUserId = record?.assignedTo ?? "";

    const selectedUserLabel = userOptions.find(
        u => String(u.value) === String(selectedUserId)
    )?.label || "Unassigned";

    const employeeOptions = userOptions.map(u =>
        `<option value="${escapeHTML(u.label)}"></option>`
    ).join("");

    const assignedToField = `
        <div class="field">
            <label>Assigned to</label>
            <input
                type="text"
                id="assignedToSearch"
                list="assignedToOptions"
                value="${escapeHTML(selectedUserLabel)}"
                placeholder="Search employee name or staff code"
            >
            <datalist id="assignedToOptions">
                <option value="Unassigned"></option>
                ${employeeOptions}
            </datalist>
            <input
                type="hidden"
                name="assignedTo"
                id="assignedTo"
                value="${escapeHTML(selectedUserId)}"
            >
        </div>
    `;

    html = field("Asset name","name","text",record?.name||"")
        + field("Asset tag","tag","text",record?.tag||"")
        + field("Serial number","serial","text",record?.serial||"")
        + field("Category","category","select",record?.category||"Laptop",["Laptop","Desktop","Monitor","Printer","Accessory","Network device","Other"].map(x=>({value:x,label:x})))
        + assignedToField
        + field("Status","status","select",record?.status||(record?.assignedTo?"Assigned":"Available"),["Available","Assigned","Maintenance"].map(x=>({value:x,label:x})));
  
}else if(type==="ticket"){
    const userOptions = data.users.map(u => ({
        value: u.id,
        label: `${u.name} (${u.staffCode || ""})`
    }));

    const selectedUserId = record?.reportedBy ?? data.users[0]?.id ?? "";

    const selectedUserLabel = userOptions.find(
        u => String(u.value) === String(selectedUserId)
    )?.label || "";

    const employeeOptions = userOptions.map(u =>
        `<option value="${escapeHTML(u.label)}"></option>`
    ).join("");

    const reportedByField = `
        <div class="field">
            <label>Reported by</label>
            <input
                type="text"
                id="reportedBySearch"
                list="reportedByOptions"
                value="${escapeHTML(selectedUserLabel)}"
                placeholder="Type an employee name or staff code"
                required
            >
            <datalist id="reportedByOptions">
                ${employeeOptions}
            </datalist>
            <input
                type="hidden"
                name="reportedBy"
                id="reportedBy"
                value="${escapeHTML(selectedUserId)}"
            >
        </div>
    `;

    html = field("Issue title","title","text",record?.title||"",null,true)
        + reportedByField
        + field("Priority","priority","select",record?.priority||"Medium",["Low","Medium","High"].map(x=>({value:x,label:x})))
        + field("Status","status","select",record?.status||"Open",["Open","In Progress","Resolved"].map(x=>({value:x,label:x})))
        + field("Description","description","textarea",record?.description||"",null,true);

 
  }else{
    html=field("Staff code","staffCode","text",record?.staffCode||"")
    +field("Full name","name","text",record?.name||"")
    +field("Email address","email","email",record?.email||"")
    +field("Department","department","text",record?.department||"")
    +field("Role","role","select",record?.role||"Employee",["Employee","IT Support","Administrator"].map(x=>({value:x,label:x})));
}
  fields.innerHTML=html;
  document.getElementById("modalEyebrow").textContent=record?"EDIT RECORD":"NEW RECORD";
  document.getElementById("modalTitle").textContent=`${record?"Edit":"Add"} ${type==="asset"?"asset":type==="ticket"?"ticket":"user"}`;
  document.getElementById("saveRecord").textContent=record?"Save changes":"Create record";
  document.getElementById("modalBackdrop").classList.remove("hidden");

  if (type === "asset") {
    const searchInput = document.getElementById("assignedToSearch");
    const employeeIdInput = document.getElementById("assignedTo");

    searchInput.addEventListener("input", () => {
        const searchValue = searchInput.value.trim();

        if (searchValue.toLowerCase() === "unassigned") {
            employeeIdInput.value = "";
            return;
        }

        const selectedEmployee = data.users.find(user => {
            const label = `${user.name} (${user.staffCode || ""})`;

            return label.toLowerCase() === searchValue.toLowerCase();
        });

        employeeIdInput.value = selectedEmployee
            ? selectedEmployee.id
            : "";
    });
}

  if (type === "ticket") {
    const searchInput = document.getElementById("reportedBySearch");
    const employeeIdInput = document.getElementById("reportedBy");

    searchInput.addEventListener("input", () => {
        const selectedEmployee = data.users.find(user => {
            const label = `${user.name} (${user.staffCode || ""})`;

            return label.toLowerCase() === searchInput.value.trim().toLowerCase();
        });

        employeeIdInput.value = selectedEmployee
            ? selectedEmployee.id
            : "";
    });
}


}
function closeForm(){document.getElementById("modalBackdrop").classList.add("hidden");document.getElementById("recordForm").reset();editing=null;currentFormType=null}


async function saveForm(event) {
    event.preventDefault();

    const values = Object.fromEntries(
        new FormData(event.target).entries()
    );

    if (currentFormType === "ticket") {
    if (!values.reportedBy) {
        showToast("Please select a valid employee from the suggestions.");
        return;
    }
}

    const formType = currentFormType;
    const isEditing = Boolean(editing);
    const recordId = editing;

    try {
        // SAVE OR UPDATE USER
        if (formType === "user") {
            const payload = {
                staff_code: values.staffCode,
                name: values.name,
                email: values.email,
                department: values.department,
                role: values.role
            };

            await apiRequest(
                isEditing ? `/users/${recordId}` : "/users",
                {
                    method: isEditing ? "PUT" : "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                }
            );

            await loadUsersFromAPI();

            closeForm();
            renderAll();

            showToast(`User ${isEditing ? "updated" : "created"} successfully.`);
            return;
        }

        // SAVE OR UPDATE ASSET
        if (formType === "asset") {
            const assignedTo = values.assignedTo
                ? Number(values.assignedTo)
                : null;

            let status = values.status;

            if (assignedTo && status === "Available") {
                status = "Assigned";
            }

            if (!assignedTo && status === "Assigned") {
                status = "Available";
            }

            const payload = {
                name: values.name,
                tag: values.tag,
                serial: values.serial || null,
                category: values.category,
                assigned_to: assignedTo,
                status: status
            };

            await apiRequest(
                isEditing ? `/assets/${recordId}` : "/assets",
                {
                    method: isEditing ? "PUT" : "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                }
            );

            await loadAssetsFromAPI();

            closeForm();
            renderAll();

            showToast(`Asset ${isEditing ? "updated" : "created"} successfully.`);
            return;
        }

       
if (formType === "ticket") {
    const payload = {
        title: values.title,
        description: values.description,
        reported_by: values.reportedBy ? Number(values.reportedBy) : null,
        priority: values.priority,
        status: values.status,
        date_raised: isEditing
            ? data.tickets.find(t => t.id === Number(recordId))?.date
            : new Date().toISOString().slice(0, 10)
    };

    await apiRequest(
        isEditing ? `/tickets/${recordId}` : "/tickets",
        {
            method: isEditing ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        }
    );

    await loadTicketsFromAPI();

    closeForm();
    renderAll();

    showToast(`Ticket ${isEditing ? "updated" : "created"} successfully.`);
    return;
}


    } catch (error) {
        console.error("Save error:", error);
        showToast(error.message || "Could not save record.");
    }
}


function deleteRecord(type,id){
  const item=data[`${type}s`].find(x=>x.id===Number(id));
  if(!item||!confirm(`Delete this ${type}? This action cannot be undone.`))return;
  data[`${type}s`]=data[`${type}s`].filter(x=>x.id!==Number(id));
  if(type==="user"){
    data.assets.forEach(a=>{if(a.assignedTo===Number(id)){a.assignedTo=null;if(a.status==="Assigned")a.status="Available";}});
  }
  saveData();renderAll();showToast(`${type[0].toUpperCase()+type.slice(1)} deleted.`);
}
document.addEventListener("click",e=>{
  const nav=e.target.closest("[data-page]");if(nav){showPage(nav.dataset.page);return;}
  const goto=e.target.closest("[data-goto]");if(goto){showPage(goto.dataset.goto);return;}
  const action=e.target.closest("[data-action]");if(action){openForm(action.dataset.action.replace("add-",""));return;}
  const edit=e.target.closest("[data-edit]");if(edit){openForm(edit.dataset.edit,edit.dataset.id);return;}
  const del=e.target.closest("[data-delete]");if(del){deleteRecord(del.dataset.delete,del.dataset.id);return;}
});
document.getElementById("recordForm").addEventListener("submit",saveForm);
document.getElementById("closeModal").addEventListener("click",closeForm);
document.getElementById("cancelModal").addEventListener("click",closeForm);
document.getElementById("modalBackdrop").addEventListener("click",e=>{if(e.target.id==="modalBackdrop")closeForm()});
["assetSearch","assetFilter"].forEach(id=>document.getElementById(id).addEventListener("input",renderAssets));
["ticketSearch","ticketFilter"].forEach(id=>document.getElementById(id).addEventListener("input",renderTickets));
document.getElementById("userSearch").addEventListener("input",renderUsers);
document.getElementById("mobileMenu").addEventListener("click",()=>document.getElementById("sidebar").classList.toggle("open"));
document.getElementById("todayDate").textContent=new Intl.DateTimeFormat("en",{weekday:"short",day:"numeric",month:"short",year:"numeric"}).format(new Date());

async function initializeApp() {
    try {
        await Promise.all([
            loadUsersFromAPI(),
            loadAssetsFromAPI(),
            loadTicketsFromAPI()
        ]);

        renderAll();

    } catch (error) {
        console.error("Application loading error:", error);
    }
}

initializeApp();
