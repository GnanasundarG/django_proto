"use strict";(self.webpackChunkAMS=self.webpackChunkAMS||[]).push([[560],{560:(S,p,o)=>{o.r(p),o.d(p,{LayoutModule:()=>L});var r=o(6814),l=o(698),m=o(1896),n=o(5879),u=o(1301),c=o(3305),s=o(3814);function v(e,a){if(1&e&&(n.TgZ(0,"div",24),n._uU(1),n.qZA()),2&e){const t=a.$implicit;n.Q6J("routerLink",t.link),n.xp6(1),n.hij(" ",t.name," ")}}function h(e,a){if(1&e&&(n.TgZ(0,"mat-expansion-panel",20)(1,"mat-expansion-panel-header",21)(2,"mat-panel-title",22),n._uU(3),n.qZA()(),n.YNc(4,v,2,2,"div",23),n.qZA()),2&e){const t=n.oxw(2).$implicit;n.xp6(2),n.Q6J("routerLink",t.link),n.xp6(1),n.hij(" ",t.name," "),n.xp6(1),n.Q6J("ngForOf",t.submenu)}}function _(e,a){if(1&e&&(n.ynx(0),n.TgZ(1,"mat-accordion",1),n.YNc(2,h,5,3,"mat-expansion-panel",19),n.qZA(),n.BQk()),2&e){const t=n.oxw(3).$implicit,i=n.MAs(3);n.xp6(2),n.Q6J("ngIf",t.menus)("ngIfElse",i)}}function x(e,a){if(1&e&&(n.TgZ(0,"span",25),n._uU(1),n.qZA()),2&e){const t=n.oxw().$implicit;n.Q6J("routerLink",t.link),n.xp6(1),n.Oqu(t.name)}}function C(e,a){if(1&e&&(n.TgZ(0,"span",16),n.YNc(1,_,3,2,"ng-container",17),n.YNc(2,x,2,2,"ng-template",null,18,n.W1O),n.qZA()),2&e){const t=a.$implicit,i=n.MAs(3);n.xp6(1),n.Q6J("ngIf",t.submenu)("ngIfElse",i)}}function M(e,a){if(1&e&&(n.TgZ(0,"mat-expansion-panel",10)(1,"mat-expansion-panel-header",11)(2,"mat-panel-title")(3,"div",12)(4,"div",5),n._UZ(5,"img",13),n.qZA(),n.TgZ(6,"div",14),n._uU(7),n.qZA()()()(),n.YNc(8,C,4,2,"span",15),n.qZA()),2&e){const t=n.oxw().$implicit;n.xp6(5),n.Q6J("src",t.icon,n.LSH),n.xp6(2),n.hij(" ",t.name," "),n.xp6(1),n.Q6J("ngForOf",t.menus)}}function f(e,a){if(1&e&&(n.TgZ(0,"div",26)(1,"div",5),n._UZ(2,"img",13),n.qZA(),n.TgZ(3,"div",14),n._uU(4),n.qZA()()),2&e){const t=n.oxw().$implicit;n.Q6J("routerLink",t.link),n.xp6(2),n.Q6J("src",t.icon,n.LSH),n.xp6(2),n.Oqu(t.name)}}function O(e,a){if(1&e&&(n.ynx(0),n.YNc(1,M,9,3,"mat-expansion-panel",8),n.YNc(2,f,5,3,"ng-template",null,9,n.W1O),n.BQk()),2&e){const t=a.$implicit,i=n.MAs(3);n.xp6(1),n.Q6J("ngIf",t.menus)("ngIfElse",i)}}let P=(()=>{class e{constructor(t,i){this.loginService=t,this.router=i}ngOnInit(){}signout(){this.loginService.deleteToken(),this.router.navigate([""])}}return e.\u0275fac=function(t){return new(t||e)(n.Y36(u.r),n.Y36(m.F0))},e.\u0275cmp=n.Xpm({type:e,selectors:[["app-sidenav"]],inputs:{navMenuItems:"navMenuItems"},decls:9,vars:1,consts:[["fxLayout","column",1,"side-nav-div"],[1,"app-nav-accordion","ams-sidenav-item"],[4,"ngFor","ngForOf"],[1,"spacer"],["fxLayout","row","fxLayoutAlign","start center",1,"sign-out-div"],[1,"logo-image"],["src","../https://testimagestore.blob.core.windows.net/assets/Sign Out.svg","height","36px",1,"logo"],[1,"signout",3,"click"],["class","mat-elevation-z0 ams-menu-expansion",4,"ngIf","ngIfElse"],["mainmenu",""],[1,"mat-elevation-z0","ams-menu-expansion"],[1,"ams-menu-panel-header"],["fxLayout","row","fxLayoutAlign","start center"],["height","36px",1,"logo",3,"src"],[1,"ams-sidenav-item-subheading"],["mat-list-item","","class","main-menu-expansion",4,"ngFor","ngForOf"],["mat-list-item","",1,"main-menu-expansion"],[4,"ngIf","ngIfElse"],["submenu",""],["class","mat-elevation-z0 ams-submenu-expansion",4,"ngIf","ngIfElse"],[1,"mat-elevation-z0","ams-submenu-expansion"],[1,"ams-submenu-expansion-header"],[1,"subitem-name",3,"routerLink"],["mat-list-item","","class","ams-submenu-text second-sub-item-test cursor-pointer",3,"routerLink",4,"ngFor","ngForOf"],["mat-list-item","",1,"ams-submenu-text","second-sub-item-test","cursor-pointer",3,"routerLink"],[1,"ams-mainmenu-text","subitem-name","cursor-pointer",3,"routerLink"],["fxLayout","row","fxLayoutAlign","start center",1,"main-menu","cursor-pointer",3,"routerLink"]],template:function(t,i){1&t&&(n.TgZ(0,"div",0)(1,"mat-accordion",1),n.YNc(2,O,4,2,"ng-container",2),n.qZA(),n._UZ(3,"span",3),n.TgZ(4,"div",4)(5,"div",5),n._UZ(6,"img",6),n.qZA(),n.TgZ(7,"span",7),n.NdJ("click",function(){return i.signout()}),n._uU(8," Sign Out "),n.qZA()()()),2&t&&(n.xp6(2),n.Q6J("ngForOf",i.navMenuItems))},dependencies:[r.sg,r.O5,m.rH,c.pp,c.ib,c.yz,c.yK,s.xw,s.Wh],styles:[".ams-sidenav-item[_ngcontent-%COMP%]{font-size:14px;color:var(--ams-text-primary)}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-subheading[_ngcontent-%COMP%]{padding:5px;font-weight:600;text-transform:uppercase;color:var(--ams-text-primary)}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link[_ngcontent-%COMP%]{padding:12px var(--padding-page);text-decoration:none;color:var(--ams-text-primary);transition:all .5s}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link[_ngcontent-%COMP%]   .link-icon[_ngcontent-%COMP%]{margin-right:16px}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link[_ngcontent-%COMP%]   span[_ngcontent-%COMP%]{line-height:24px}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link.disabled[_ngcontent-%COMP%]{color:#ffffff2e;cursor:pointer;pointer-events:none}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link[_ngcontent-%COMP%]:hover, .ams-sidenav-item[_ngcontent-%COMP%]   .ams-sidenav-item-link.active[_ngcontent-%COMP%]{background:rgba(0,0,0,.3);color:var(--ams-text-primary)}.ams-sidenav-item[_ngcontent-%COMP%]   .logo-image[_ngcontent-%COMP%]   .logo[_ngcontent-%COMP%]{height:100%;padding:5px}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-menu-expansion[_ngcontent-%COMP%]{background-color:inherit}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-menu-expansion[_ngcontent-%COMP%]     .mat-expansion-panel-content .mat-expansion-panel-body{padding-right:0;padding-left:13%;padding-bottom:0;min-height:48px}.ams-sidenav-item[_ngcontent-%COMP%]   .main-menu[_ngcontent-%COMP%]{height:48px}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-submenu-expansion[_ngcontent-%COMP%]     .mat-expansion-panel-content .mat-expansion-panel-body{padding-right:0;padding-left:2%;padding-top:5%}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-submenu-expansion[_ngcontent-%COMP%]   .ams-submenu-text[_ngcontent-%COMP%]{padding-left:10px;height:35px}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-menu-panel-header[_ngcontent-%COMP%]{padding-left:0}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-menu-panel-header.mat-expanded[_ngcontent-%COMP%]{height:var(--mat-expansion-header-collapsed-state-height)}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-submenu-expansion[_ngcontent-%COMP%]{background-color:inherit}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-submenu-expansion[_ngcontent-%COMP%]   .ams-submenu-expansion-header[_ngcontent-%COMP%]{padding-left:2%}.ams-sidenav-item[_ngcontent-%COMP%]   .ams-submenu-expansion[_ngcontent-%COMP%]   .ams-submenu-expansion-header.mat-expanded[_ngcontent-%COMP%]{height:var(--mat-expansion-header-collapsed-state-height)}.ams-sidenav-item[_ngcontent-%COMP%]   .main-menu-expansion[_ngcontent-%COMP%]   .subitem-name[_ngcontent-%COMP%]{color:var(--ams-text-secondary);font-weight:500}.ams-sidenav-item[_ngcontent-%COMP%]   .main-menu-expansion[_ngcontent-%COMP%]   .second-sub-item-test[_ngcontent-%COMP%]{color:var(--ams-text-secondary);font-weight:500;margin-bottom:8px}.sign-out-div[_ngcontent-%COMP%]{cursor:pointer;height:48px}.sign-out-div[_ngcontent-%COMP%]   .logo-image[_ngcontent-%COMP%]   .logo[_ngcontent-%COMP%]{height:100%;padding:5px}.sign-out-div[_ngcontent-%COMP%]   .signout[_ngcontent-%COMP%]{color:var(--ams-text-secondary);font-weight:500}.side-nav-div[_ngcontent-%COMP%]{height:100%}.spacer[_ngcontent-%COMP%]{flex:1 1 auto}.app-nav-accordion[_ngcontent-%COMP%]   .mat-expansion-panel[_ngcontent-%COMP%]{border-radius:0!important;box-shadow:none!important}.app-nav-accordion[_ngcontent-%COMP%]   .mat-expansion-panel.mat-expansion-panel-spacing[_ngcontent-%COMP%]{margin:0}.app-nav-accordion[_ngcontent-%COMP%]   .mat-expansion-panel[_ngcontent-%COMP%]   .mat-expansion-panel-body[_ngcontent-%COMP%]{padding:0}"]}),e})();var b=o(1274);let y=(()=>{class e{constructor(){this.inputValue=""}}return e.\u0275fac=function(t){return new(t||e)},e.\u0275cmp=n.Xpm({type:e,selectors:[["app-header"]],decls:12,vars:0,consts:[[1,"ams-toolbar"],["src","https://testimagestore.blob.core.windows.net/assets/logo (1).svg",1,"logo","img"],[1,"spacer"],["fxFlex","400px","fxLayout","row","fxLayoutAlign","start center",1,"ams-search-field"],["src","https://testimagestore.blob.core.windows.net/assets/Search.svg",1,"img"],["fxFlex","","placeholder","Search for airlines, schedules..",1,"ams-search-input"],[1,"ams-notification"],["src","https://testimagestore.blob.core.windows.net/assets/notification.svg",1,"img","cursor-pointer"],[1,"ams-profile"],["src","https://testimagestore.blob.core.windows.net/assets/Profile Tick.svg",1,"img","cursor-pointer"]],template:function(t,i){1&t&&(n.TgZ(0,"mat-toolbar",0),n._UZ(1,"img",1),n.TgZ(2,"span"),n._uU(3,"Welcome to Smart Airports"),n.qZA(),n._UZ(4,"span",2),n.TgZ(5,"div",3),n._UZ(6,"img",4)(7,"input",5),n.qZA(),n.TgZ(8,"div",6),n._UZ(9,"img",7),n.qZA(),n.TgZ(10,"div",8),n._UZ(11,"img",9),n.qZA()())},dependencies:[b.Ye,s.xw,s.Wh,s.yH],styles:[".spacer[_ngcontent-%COMP%]{flex:1 1 auto}.ams-toolbar[_ngcontent-%COMP%]{background-color:var(--ams-white);border-bottom:1px solid rgb(192,187,187)}.ams-search-field[_ngcontent-%COMP%]{margin-right:10px;background-color:var(--ams-grey)}.ams-search-field[_ngcontent-%COMP%]   input[_ngcontent-%COMP%]{background:var(--ams-grey)}.ams-notification[_ngcontent-%COMP%]{margin-right:10px}.logo[_ngcontent-%COMP%]{height:130%}"]}),e})();var g=o(2651);let Z=(()=>{class e{constructor(){this.navMenuItems=[{name:"Dashboard",icon:"https://testimagestore.blob.core.windows.net/assets/Dashboard.svg",link:["/layout/dashboard"],header:!0},{name:"Forecasting",icon:"https://testimagestore.blob.core.windows.net/assets/calendar-8.svg",header:!0,menus:[{name:"Schedule based",submenu:[{name:"Arrival & Departure",link:["/layout/forecasting/schedule-based/depart-arri-night"]},{name:"Hourly Movement",link:["/layout/forecasting/schedule-based/hourly-movement"]},{name:"Day wise",link:["/layout/forecasting/schedule-based/day-wise"]},{name:"Origin & Destination Wise",link:["/layout/forecasting/schedule-based/origin-and-destination"]},{name:"Seat & Flight Wise",link:["/layout/forecasting/schedule-based/aircraft-seat-and-flight-count"]},{name:"Pax Movement",link:["/layout/forecasting/schedule-based/pax-movement"]},{name:"OverNight Parking",link:["/layout/forecasting/schedule-based/overnight-parking-summary"]},{name:"Airlines & Aircraft",link:["/layout/forecasting/schedule-based/airlines-aircraft"]},{name:"Flight wise count",link:["/layout/forecasting/schedule-based/flights-count"]}]}]},{name:"Configuration",icon:"https://testimagestore.blob.core.windows.net/assets/Configuration.svg",header:!0,menus:[{name:"Gates"}]}]}}return e.\u0275fac=function(t){return new(t||e)},e.\u0275cmp=n.Xpm({type:e,selectors:[["app-layout"]],decls:10,vars:1,consts:[["fxLayout","column","fxFill","",1,"app-container"],[1,"header-toolbar"],[1,"sidenav-bar"],[1,"ams-sidenav-container"],["color","primary","mode","side","opened","",1,"ams-sidenav"],["drawer",""],[3,"navMenuItems"],[1,"ams-sidenav-content"]],template:function(t,i){1&t&&(n.TgZ(0,"div",0)(1,"div",1),n._UZ(2,"app-header"),n.qZA(),n.TgZ(3,"div",2)(4,"mat-sidenav-container",3)(5,"mat-sidenav",4,5),n._UZ(7,"app-sidenav",6),n.qZA(),n.TgZ(8,"mat-sidenav-content",7),n._UZ(9,"router-outlet"),n.qZA()()()()),2&t&&(n.xp6(7),n.Q6J("navMenuItems",i.navMenuItems))},dependencies:[m.lC,P,y,g.JX,g.TM,g.Rh,s.xw,s.s9],styles:[".app-container[_ngcontent-%COMP%]{position:absolute;inset:0}.app-container[_ngcontent-%COMP%]   .header-toolbar[_ngcontent-%COMP%]{width:100%}.app-container[_ngcontent-%COMP%]   .sidenav-bar[_ngcontent-%COMP%]{height:100%}.app-container[_ngcontent-%COMP%]   .logo-image[_ngcontent-%COMP%]{height:4.5em}.app-container[_ngcontent-%COMP%]   .logo-image[_ngcontent-%COMP%]   .logo[_ngcontent-%COMP%]{height:100%;background:var(--ams-accent-100);width:100%}.app-container[_ngcontent-%COMP%]   .ams-toolbar[_ngcontent-%COMP%]{background:#fff;border-bottom:1px solid #ddd;color:var(--si-primary-500)}.app-container[_ngcontent-%COMP%]   .ams-toolbar[_ngcontent-%COMP%]   .mat-toolbar-row[_ngcontent-%COMP%]{padding:0}.app-container[_ngcontent-%COMP%]   .ams-toolbar[_ngcontent-%COMP%]   .mat-toolbar-row[_ngcontent-%COMP%] > button[_ngcontent-%COMP%]{height:100%;border-radius:0}.app-container[_ngcontent-%COMP%]   .ams-sidenav-container[_ngcontent-%COMP%]{height:100%}.app-container[_ngcontent-%COMP%]   .ams-sidenav-container[_ngcontent-%COMP%]   .ams-sidenav[_ngcontent-%COMP%]{min-width:260px;padding:var(--padding-page) 0;background:var(--ams-accent-100);color:#fff}.app-container[_ngcontent-%COMP%]   .ams-sidenav-container[_ngcontent-%COMP%]   .ams-sidenav-content[_ngcontent-%COMP%]{overflow:hidden;width:80%}.app-container[_ngcontent-%COMP%]   .spacer[_ngcontent-%COMP%]{flex:1 1 auto}"]}),e})();var d=o(980);const A=[{path:"",component:Z,children:[{path:"",redirectTo:"dashboard",pathMatch:"full"},{path:"dashboard",loadChildren:()=>o.e(716).then(o.bind(o,7716)).then(e=>e.DashboardModule),canActivate:[d.p]},{path:"forecasting",loadChildren:()=>o.e(683).then(o.bind(o,1683)).then(e=>e.ForecastingModule),canActivate:[d.p]}]}];let T=(()=>{class e{}return e.\u0275fac=function(t){return new(t||e)},e.\u0275mod=n.oAB({type:e}),e.\u0275inj=n.cJS({imports:[m.Bz.forChild(A),m.Bz]}),e})();var k=o(6652),w=o(1447);let L=(()=>{class e{}return e.\u0275fac=function(t){return new(t||e)},e.\u0275mod=n.oAB({type:e}),e.\u0275inj=n.cJS({imports:[r.ez,T,l.m,k.q,w.o9]}),e})()}}]);