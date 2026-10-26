var image_ajaxLoading, image_ajaxLoading2, IPH_CONT_OFF_IMG, IPH_CONT_ON_IMG;
var IPH_SWITCH_IMG, FANCY_ERR_IMG, image_Color_Picker_Url, DATEPICKER_PREV_URL;
var DATEPICKER_NEXT_URL, TAB_OFF_IMG, TAB_ON_IMG, ITEM_SPEC_URL = "";
var SHORT_GRID_CELL_TXT = {};
//Global eboObject
var ebo = {};

function getParentAndTabQryString() {
    if (tabQryString == "") return parentQryString;
    return parentQryString + "&" + tabQryString
}

function DataGrid_SingleRecordPager_PageChanged(newPageIndex) {
    goPage(pageURL, 'phi=' + newPageIndex + getParentAndTabQryString() + '&se=' + childGridQueryString + "&fe=" + childfilterQueryString)
}

function DataGrid_Pager_PageChanged(newPageIndex) {
    goPage(pageURL, 'pi=' + newPageIndex + "&se=" + gridQueryString + "&fe=" + filterQueryString + getParentAndTabQryString() )
}

function DataGrid_Pager_KeyPressed(event, maxPageNumber) {
    ToolbarPager_KeyPressed(event, maxPageNumber, DataGrid_Pager_PageChanged);
}

function DataGrid_Pager_PagerEdit(e, mpi, inName, Pager_PageChanged) {
    var key=e.keyCode || e.which;
     if (key==13){    
        var pi = $("input[name='" + inName + "']").val();
        
        if(isNaN(pi) || pi <= 0){
            pi = 0;        
        }else if (pi > mpi){
            pi = mpi - 1;
        }else {
            pi = Math.ceil(pi) - 1; 
        }
                       
        Pager_PageChanged(pi)
    }
}

function DataGrid_Sort(grdExpr) {
    goPage(pageURL, 'se=' + grdExpr + "&fe=" + filterQueryString + getParentAndTabQryString())
}

function ToolbarPager_KeyPressed(event, maxPageNumber, changeFunction) {
    if (event.keyCode === 13) {
        var inputTarget = $(event.target);
        if (UIUtils.IsValid(inputTarget)) {
            var inputValue = inputTarget.val();
            if (UIUtils.IsValid(inputValue)) {
                var pageNumber = parseInt(inputValue);
                if (inputValue.charAt(0) === '+'
                    || inputValue.charAt(0) === '-'
                    || (parseFloat(inputValue) !== parseInt(inputValue)) && !isNaN(inputValue)
                    || ((parseFloat(inputValue) === parseInt(inputValue)) && !isNaN(inputValue) && parseInt(inputValue) < 1)
                    || isNaN(inputValue))
                    $("#dialog").ebomodal({ modalType: "Close", modalText: ult_locale.CLNT_SCRIPT_13 });
                else if (pageNumber > maxPageNumber)
                    $("#dialog").ebomodal({ modalType: "Close", modalText: ult_locale.CLNT_SCRIPT_14 });
                else
                    changeFunction(pageNumber - 1);
            }
        }
    }
}

function ToolbarPager_TabClick(newTabIndex, tabIndex, key) {
}

function goPage(pgURL, qryStr) {
    if (arguments.length < 2) qryStr = "";
    window.location.href = ((qryStr == "") ? pgURL : ((pgURL.indexOf("?") > -1) ? (pgURL + "&" + qryStr) : (pgURL + '?' + qryStr)));
}

function goPageNewTab(pgURL, qryStr) {
    if (arguments.length < 2) qryStr = "";

    window.open(
      ((qryStr == "") ? pgURL : ((pgURL.indexOf("?") > -1) ? (pgURL + "&" + qryStr) : (pgURL + '?' + qryStr))),
      '_blank'
    );
}

function ClosestatusMsg(elementID) {
    var obj = document.getElementById(elementID)
    if (obj){ obj.style.display = "none"}
}

function S4() {
    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
}
function guid() {
    return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4());
} 

String.prototype.format = function() {
    var s = this, i = arguments.length;
    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

String.prototype.endsWith = function(suffix) {
    return (this.substr(this.length - suffix.length) === suffix);
}

String.prototype.startsWith = function(prefix) {
    return (this.substr(0, prefix.length) === prefix);
}

String.prototype.template = function(o, pf, trunc) {

    if (arguments.length < 3) trunc = true;
    return this.replace(/{([^{}]*)}/g,
        function(a, b) {
            if (o[pf.toLowerCase() + b.toLowerCase()]) b = pf + b;
            var r = o[b.toLowerCase()];
            if (!r) r = "&nbsp;";
            if (trunc && r.length > 30) r = r.substring(0, 30) + "...";
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    )
};

    String.prototype.uniqueID = function(count) {
        if (arguments.length < 1) count = 16;
        if (count > 16) count = 16;
        var ar = [], HEX = '0123456789ABCDEF';
        var i = 0;
        for (i = 0; i < count; i++) ar[i] = Math.floor(Math.random() * 0x10);
        for (i = 0; i < count; i++) ar[i] = HEX.charAt(ar[i]);
        return ar.join('');
    }

function hideTb(ftlN, pgID, url) {
    $('div#FFBgMax').slideUp('slow');
    $('div#FFBgMin').slideDown('slow');
    $("#FixedFooterBg").show(0);
    postPanelStatus("OFF", ftlN, pgID, url, null);
}
function showTb(ftlN, pgID, url) {
    $('div#FFBgMax').slideDown('slow');
    $('div#FFBgMin').slideUp('slow');
    $("#FixedFooterBg").hide(0);
    postPanelStatus("ON", ftlN, pgID, url, null);
}

/*
(state, filterControlName, pageID, url, callback)
*/
function postPanelStatus(state, ftlN, pgID, url, callback, colid, sort) {
    if (arguments.length < 6) { colid = "0";sort = "0"; }
    var data = { pid: pgID, pnID: ftlN, colID: colid, srt: sort, pnsts: state };
    if(callback == null || !callback) callback =  rtnPanelStatus;
    $.post(url, data, callback, "json");
}

function rtnPanelStatus(jdata){ }

jQuery.format = function jformat(text) {
    if (arguments.length <= 1) { return text; }
    var tokenCount = arguments.length - 2;
    for (var token = 0; token <= tokenCount; ++token) {
        text = text.replace(new RegExp("\\{" + token + "\\}", "gi"), arguments[token + 1]);
    }
    return text;
};

function isIPhoneOrIPad() {
    return (navigator.platform == "iPhone" ||  navigator.platform == "iPad")
}

var startTCHX = 0, curTCHX = 0
function TCHS() {
    if (!isIPhoneOrIPad()) return;
    startTCHX = event.touches[0].pageX
}
function TCHM() {
    if (!isIPhoneOrIPad()) return;
    curTCHX = event.targetTouches[0].pageX - startTCHX
}
function TCHE(id) {
    if (!isIPhoneOrIPad()) return;
    if (startTCHX >= curTCHX) {        
        $("table[id='" + id + "'][pid='Pager'] tr td a span.tbrNext").parent("a").parent("td").click()
    }
    else {
        $("table[id='" + id + "'][pid='Pager'] tr td a span.tbrPrev").parent("a").parent("td").click()
    }
    startTCHX = 0
}

function delcv(url) {
    $("#dialog").ebomodal({ modalType: "OkCancel", modalText: ult_locale.CLNT_SCRIPT_1, saveButtonAction: function () { goPage(url, ''); } });
}

function delcf(url) {
    $("#dialog").ebomodal({ modalType: "OkCancel", modalText: ult_locale.CLNT_SCRIPT_2, saveButtonAction: function () { goPage(url, ''); } });
}

function delfav(gid) {
    $("#dialog").ebomodal({
        modalType: "OkCancel",
        modalText: ult_locale.CLNT_SCRIPT_3,
        saveButtonAction: function () {
            goPage(unescape(DEL_FAV_URL), 'gid=' + escape(gid));
        }
    });
}

function Replace(s, fs, rs) {
    var sRtn = "";
    var sSrc = new String(s).toString(), sOrgs = new String(s);
    var nPos = sOrgs.toString().indexOf(fs);
    while (nPos > -1) {
        sRtn += sSrc.substring(0, nPos) + rs;
        sOrgs = sOrgs.substring(nPos + fs.length);
        sSrc = sSrc.substring(nPos + fs.length);
        nPos = sOrgs.indexOf(fs);
    }
    sRtn += sOrgs;
    return sRtn;
}

function getDate(dateVal) {
    var DATE_INPUT_FORMAT_MDY = 0
    var DATE_INPUT_FORMAT_DMY = 1
    var DATE_INPUT_FORMAT_YMD = 2
    dateVal = new String(dateVal).split(" ")[0];
    var arrRaw = dateVal.split(dtSeparator)

    //Assume m/d/y format.
    if (arrRaw.length > 0) mon = arrRaw[0];
    else mon = defMonth;
    if (arrRaw.length > 1) day = arrRaw[1];
    else day = 1;
    if (arrRaw.length > 2) year = arrRaw[2];
    else year = 0;


    switch (dtFormat) {
        case DATE_INPUT_FORMAT_DMY:
            n = mon; mon = day; day = n;
            break;
        case DATE_INPUT_FORMAT_YMD:
            n = year; year = day; day = n;
            n = mon; mon = year; year = n;
            break;
    }

    if (parseInt(year, 10) >= 0 && parseInt(year, 10) <= 99) {
        year = parseInt(year, 10) + 2000; // if two digit year is given then bias it with 2000.
    }

    return new Array(year, mon - 1, day)
}

function getDateEx(str) {
    var tmp = getDate(str)
    dt1 = new Date(tmp[0], tmp[1], tmp[2]);
    return dt1;
}

/*************************************************************************/

/* Added By Viswanath.s for date range testing */
function checkDate(adate) {
    if (adate == "") {
        alert(ult_locale.CLNT_SCRIPT_4);
        return false;
    }
    var dt = Date.parse(adate);
    if (dt == null) {
        alert(ult_locale.CLNT_SCRIPT_5);
        return false;
    }
    return true;
}

function checkDateRange(range) {
    if (range == "") {
        alert(ult_locale.CLNT_SCRIPT_6);
        return false;
    }
    var parts = range.split("-");
    if (parts.length > 2) {
        alert($.format(ult_locale.CLNT_SCRIPT_7, CUR_USR_DT_FORMAT));
        return false;
    }

    if (parts.length != 2) {
        alert($.format(ult_locale.CLNT_SCRIPT_8, CUR_USR_DT_FORMAT));
        return false;
    }
    var fromDate = Date.parse(parts[0]);
    var toDate = Date.parse(parts[1]);
    if (fromDate == null || toDate == null) {
        alert(ult_locale.CLNT_SCRIPT_9);
        return false;
    }
    if (fromDate > toDate) {
        alert(ult_locale.CLNT_SCRIPT_10);
        return false;
    }
    return true;
}

function getPreviousYearRange() {
    var dt1, dt2;
    dt1 = new Date();
    dt2 = new Date();
    dt1.setFullYear((new Date()).getFullYear() - 1, 0, 1);
    dt2.setFullYear((new Date()).getFullYear() - 1, 11, 31);
    s1 = dt1.toString(CUR_USR_DT_FORMAT);
    s2 = dt2.toString(CUR_USR_DT_FORMAT);
    s = s1 + "-" + s2;
    return s;
}


function getPast3MonthsRange() {
    //start day of this month
    var dtToday = new Date();
    var dt2 = new Date(dtToday.getFullYear(), dtToday.getMonth(), 1);
    //last dayt of last month
    dt2.setDate(dt2.getDate() - 1);
    mn = dt2.getMonth();
    yr = dt2.getFullYear();
    mn -= 2;
    var dt1 = new Date();
    dt1.setFullYear(yr, mn, 1);
    s1 = dt1.toString(CUR_USR_DT_FORMAT);
    s2 = dt2.toString(CUR_USR_DT_FORMAT);
    s = s1 + "-"+ s2;
    return s;
}

function getPastNMonthsRange(n) {
    //start day of this month
    var dtToday = new Date;
    var dt2 = dtToday;
    dt2.setFullYear(dtToday.getFullYear(), dtToday.getMonth(), 1);
    //var dt2 = new Date(dtToday.getFullYear(), dtToday.getMonth(), 1);
    //last dayt of last month
    dt2.setDate(dt2.getDate() - 1);
    mn = dt2.getMonth();
    yr = dt2.getFullYear();
    mn -= n-1;
    var dt1 = new Date;
    dt1.setFullYear(yr, mn, 1);
   // s1 = dt1.toString(CUR_USR_DT_FORMAT);
    // s2 = dt2.toString(CUR_USR_DT_FORMAT);
    s1 = fDate(dt1);
    s2 = fDate(dt2);
    s = s1 + "-" + s2;
    return s;
}
function getPastOneYearRange() {
    //start day of this month
    var dtToday = new Date();
    var dt2 = new Date(dtToday.getFullYear(), dtToday.getMonth(), 1);
    //last dayt of last month
    dt2.setDate(dt2.getDate() - 1);
    mn = dt2.getMonth();
    yr = dt2.getFullYear();
    mn -= 11;
    var dt1 = new Date();
    dt1.setFullYear(yr, mn, 1);
    s1 = dt1.toString(CUR_USR_DT_FORMAT);
    s2 = dt2.toString(CUR_USR_DT_FORMAT);
    s = s1 + "-" + s2;
    return s;
}

function ToStringFromDate(date) {
    if (!date.getDate()) return '';
    //CUR_USR_DT_FORMAT is global variable defined at PageHeadContent.aspx
    return _formatDate(date, CUR_USR_DT_FORMAT);
}

function fDate(date) {
    if (!date.getDate()) return '';
    return _formatDate(date, CUR_USR_DT_FORMAT);
}

function _formatDate(date, format) {
    var m = date.getMonth();
    var d = date.getDate();
    var y = date.getFullYear();
    var parts = format.split(''), part;
    for (var i = 0; i < parts.length; i++) {
        part = parts[i];
        switch (parts[i]) {
            case 'd':
                part = (d < 10) ? ("0" + d) : d;
                break;
            case 'm':
                part = (m < 9) ? ("0" + (1 + m)) : (1 + m);
                break;
            case 'y':
            case 'Y':
                part = y;
                break;
        }
        parts[i] = part;
    }
    return parts.join('');
}

function DRangeFromToday() {
    return ToStringFromDate(new Date()) + "-" + ToStringFromDate(new Date());
}

function IsErrorInInputValue(ctrlName) {
    var hasError = $("input[name='" + ctrlName + "']").hasClass("input-validation-error");
    return hasError;
}

String.prototype.bool = function() {
    return (/^true$/i).test(this);
};

Boolean.prototype.parse = function(str) {
    switch (str.toLowerCase()) {
        case "true":
            return true;
        case "false":
            return false;
        default:
            throw new Error(ult_locale.CLNT_SCRIPT_11);
    }
};
/* functions of Viswanath are over here */
function swapTopImage(obj) {
    var tempSrc = obj.attr("src")
    obj.attr("src", obj.attr("altsrc"))
    obj.attr("altsrc", tempSrc)
}

String.prototype.padLeft = function(fill, l) {
    l = l || 2;
    var paddedLeftStr;
    if (l > this.length) {
        paddedLeftStr = new Array(l - this.length + 1).join(fill) + this;
    }
    else {
        paddedLeftStr = this;
    }
    return paddedLeftStr;
};

function Init_RndCorner_And_Status() {
    //$(".roundedbox").eboroundedcorner()
    //$(".roundedboxwhite").eboroundedcorner({ borderColor: "#fff" });
    //$(".roundedboxblue").eboroundedcorner({ borderColor: "#a1abca" });
    //$(".btnroundedbox").eboroundedcorner({ borderColor: "#f2f2f2", prependPrefixChar: "x", appendPrefixChar: "x", borderBottomColor: "#d2d2d2" });
    //$("div.StatusWarning").eboroundedcorner({ borderColor: "#ffffcc", prependPrefixChar: "w", appendPrefixChar: "w" });
    //$("div.StatusInfo").eboroundedcorner({ borderColor: "#eef", prependPrefixChar: "i", appendPrefixChar: "i" });
    //$("div.StatusError").eboroundedcorner({ borderColor: "#fdd", prependPrefixChar: "e", appendPrefixChar: "e" });
}

function ChangeBusinessUnitListener(gid) {
    var options = {
        modalType: 'Loading',
        needCloseConfirm: false,
        modalId: 'modal-loading-bu'
    };
    showModal(options);

    setTimeout(function() {
        goPage(CHG_BUS_URL, 'gid=' + gid);
    }, 1500);
}
function SwitchApplication(appCode) {
    var options = {
        modalType: 'Loading',
        needCloseConfirm: false,
        modalId: 'modal-loading-app'
    };
    showModal(options);

    setTimeout(function () {
        goPage(SWC_APP_URL, 'AppCode=' + appCode);
    }, 1500);
}
function LicenseApplication(appCode) {
    goPage(LIC_APP_URL, 'AppCode=' + appCode)
}
function ShowAppFeatures(appCode) {
    goPage(SHW_APP_FEA, 'AppCode=' + appCode)
}

var _dlg_Shw = null; //global dialog ref
function showModal(options) {
    _dlg_Shw = $('#dialog').ebomodal(options);
}

function shwLdDiag(intype, msg, onok) {
    var type = intype;
    if (type !== 'OkCancel' && type !== 'Close' && type !== 'Loading')
        type = 'OkCancel';

    var modalText = msg;
    if (arguments.length < 2) {
        type = 'Loading';
        modalText = ult_locale.CLNT_SCRIPT_12;
        onok = function () { };
    } else if (arguments.length < 3 || (type === 'Close' && arguments.length === 3)) {
        type = 'Close';
        if (arguments.length === 2)
            onok = function () { };

        _dlg_Shw = $("#dialog").ebomodal({ modalType: type, modalText: modalText, closeButtonAction: onok });
    }

    if (type !== 'Close')
        _dlg_Shw = $("#dialog").ebomodal({ modalType: type, modalText: modalText, saveButtonAction: onok });
}


function closeLdDiag() {
    if (_dlg_Shw) {
        _dlg_Shw.modal('toggle');
    }
}

function InitPage() {

    var toolbarItem = $('.ToolBar td.hasChild');
    if (UIUtils.IsValid(toolbarItem)) {
        var topOffSet = -10;
        var leftOffSet = 0;

        $.each(toolbarItem, function () {
            var currentItem = $(this);
            var currentItemGid = currentItem.attr('gid');
            var itemParentId = currentItem.closest('table.ToolBar').attr('parentid');
            if (UIUtils.IsValid(currentItemGid)) {
                var elementToRemove = $('.ui-toolbar-submenu[parentgid="' + currentItemGid + '"]');
                if (UIUtils.IsValid(elementToRemove)) {
                    $.each(elementToRemove, function() {
                        if (UIUtils.IsValid(currentItem)) {
                            if (currentItem.parent().hasClass('content'))
                                currentItem.remove();
                        }
                    });
                }

                topOffSet = -4;
                if (currentItemGid === '$FilterField' || currentItemGid === '$FilterOperator') {
                    var entryContent = elementToRemove.closest('.content.main-content.entry-master-content');
                    if (UIUtils.IsValid(entryContent)) {
                        topOffSet = -2;
                    }
                }
                if (currentItemGid === '$MoveToPage') {
                    currentItem = currentItem.find('i.movetopage-input-dd-icon');
                    topOffSet = 10;
                    if (itemParentId.indexOf('NCRCard') > -1)
                        topOffSet -= 8;

                    // When pager popup is located in home screen (Alerts pager)
                    var homeContent = elementToRemove.closest('.content.main-content.home-content');
                    if (UIUtils.IsValid(homeContent)) {
                        topOffSet = 37;
                        if (UIUtils.IsValid(itemParentId) && itemParentId === 'Alert2') {
                            //topOffSet = -10;
                        }
                    }

                    leftOffSet = -136;
                }
                currentItem.ebopopup({ isToolBarPopup: true, topOffset: topOffSet, leftOffset: leftOffSet, alignment: 'bottom' });
            }
        });
    }

    var uiPopups = $('.ui-toolbar-submenu');
    uiPopups.each(function () {
        var pop = $(this);
        if (pop.closest('div#Pager-Dashboard').length <= 0)
            pop.detach().appendTo($('.main-content'));
    });

    //debugger
    $(".cfgdd").dropdownchecklist({ zIndex: 5 });

    var menuAccordion = $("#menuAccordion");

    if (UIUtils.IsValid(menuAccordion)) {
        var accordionOpts = { header: ".accordiontitle", heightStyle: 'content', collapsible: true, active: 0 };
        var idx = UIUtils.GetFromLocalStorage('accordion-active-index');
        if (idx !== undefined) {
            accordionOpts = { header: ".accordiontitle", heightStyle: 'content', collapsible: true, active: parseInt(idx) };
            UIUtils.RemoveFromLocalStorage('accordion-active-index');
        }

        menuAccordion.accordion(accordionOpts);
    }

    $(".filterize").ebofilter();
    $(".Grid:not([isLateBind])").ebodatagrid({ "shorten": SHORT_GRID_CELL_TXT });
    $(".DetailTabPage").ebotabcontrol({ imageUrl: TAB_OFF_IMG, selImageUrl: TAB_ON_IMG });
    $(".toolbar").ebotoolbar();
    //$(".ToolBar td.hasChild").ebopopup({ isToolBarPopup: true });

    Init_RndCorner_And_Status();

    $(".TipImg").ebotooltip();

    $(".cbsu").each(function () {
        $(this).addClass("switchbusunitout");
        $(this).ebopopup({
            popupchildElementID: "#popchangebusunit", alignment: "bottom", topOffset: $(this).height(), halignment: "right", leftOffset: 2,
            aftershow: function (obj) { obj.removeClass("switchbusunitout").addClass("switchbusunitover") },
            afterhide: function (obj) { obj.addClass("switchbusunitout").removeClass("switchbusunitover") }
        })
    });

    $("#imgFavList").parent("li").addClass("favoriteout")
    $("#imgCustomViews").parent("li").addClass("favoriteout2")
    $("#imgCustomFilters").parent("li").addClass("favoriteout")
    $("#imgAlertOptions").parent("div").addClass("favoriteout3")

    $("#imgFavList").ebopopup({ popupchildElementID: "#tpFavoritesD", alignment: "bottom", topOffset: 18, halignment: "right", leftOffset: 46,
        aftershow: function(obj) { obj.parent("li").removeClass("favoriteout").addClass("favoriteover") },
        afterhide: function(obj) { obj.parent("li").addClass("favoriteout").removeClass("favoriteover") } 
    });

    $("#imgCustomViews").ebopopup({ popupchildElementID: "#customviews", alignment: "bottom", topOffset: 18, halignment: "right", leftOffset: $("#imgCustomViews").parent().width()-14,
        aftershow: function(obj) { obj.parent("li").removeClass("favoriteout2").addClass("favoriteover2") },
        afterhide: function(obj) { obj.parent("li").addClass("favoriteout2").removeClass("favoriteover2") } 
    });

    $("#imgCustomFilters").ebopopup({ popupchildElementID: "#customfilters", alignment: "bottom", topOffset: 19, halignment: "right", leftOffset: $("#imgCustomFilters").parent().width() - 15,
        aftershow: function(obj) { obj.parent("li").removeClass("favoriteout").addClass("favoriteover") },
        afterhide: function(obj) { obj.parent("li").addClass("favoriteout").removeClass("favoriteover") } 
    });

    $("#imgAlertOptions").ebopopup({
        popupchildElementID: "#alertoptions", alignment: "bottom", halignment: "right", leftOffset: -48, topOffset: 30,
        aftershow: function(obj) { obj.parent("div").removeClass("favoriteout3").addClass("favoriteover3") },
        afterhide: function(obj) { obj.parent("div").addClass("favoriteout3").removeClass("favoriteover3") } 
    });

    $(".progressbar").each(function() {
        var o = $(this), v = o.attr("value"), op = { 'value': v };
        if (o.attr("ty") == "cs") op = { 'value': v, 'HIGH':100.001, 'MEDIUM':100.001 };
        o.eboprogressbar(op);
    });

    call_focusCtlExpr();

    var objIPhoneCheckboxOptions = { switch_on_container_path: IPH_CONT_ON_IMG, switch_off_container_path: IPH_CONT_OFF_IMG, switch_path: IPH_SWITCH_IMG }
    $(".ipc").each(function() {
        $(this).iphoneSwitch($(this).attr("dval"), null, null, objIPhoneCheckboxOptions);
    });
    $(".ipced").each(function() {
        $(this).iphoneSwitch($(this).attr("dval"), null, null, objIPhoneCheckboxOptions);
    });
    $(".ipcyn").each(function() {
        $(this).iphoneSwitch($(this).attr("dval"), null, null, objIPhoneCheckboxOptions);
    });
    $(".ipctf").each(function() {
        $(this).iphoneSwitch($(this).attr("dval"), null, null, objIPhoneCheckboxOptions);
    });

    $(".jqslider").each(function() {
        var oSlider = $(this), minV = parseInt(oSlider.attr("minval"), 10), maxV = parseInt(oSlider.attr("maxval"), 10), 
        sVal = parseInt(oSlider.attr("curval"), 10), txtCtl = $("input:text[name='" + oSlider.attr("cname") + "']").css({ width: 30 });
        oSlider.slider({ orientation: "horizontal", range:"min", min: minV, max: maxV, value: sVal,
            slide: function(event, ui) { txtCtl.val(ui.value);}
        });
        txtCtl.change(function() {
            var vl = Math.round(txtCtl.val());
            txtCtl.val(vl);
            if (isNaN(vl) || vl < minV || vl > maxV) { txtCtl.val(sVal); return };
            oSlider.slider("value", vl);
        });
    });
    //trun autocomplte off
    $("input:text").attr("autocomplete", "off");
    $("input:password").attr("autocomplete", "new-password");

    // moving dialogs to body
    var dlgViewNotes = $('#dlgViewNotes');
    if (UIUtils.IsValid(dlgViewNotes)) {
        dlgViewNotes.detach().appendTo('body');
    }

    var dlgNotes = $('#dlgNotes');
    if (UIUtils.IsValid(dlgNotes)) {
        dlgNotes.detach().appendTo('body');
    }

    var dlgAttach = $('#dlgAttach');
    if (UIUtils.IsValid(dlgAttach)) {
        dlgAttach.detach().appendTo('body');
    }

    var dvToolTipParent = $('#dvToolTipParent');
    if (UIUtils.IsValid(dvToolTipParent)) {
        dvToolTipParent.detach().appendTo('.content.main-content'); // 'body'
    }

    var dvSerialInfo = $('#divSerialInfo');
    if (UIUtils.IsValid(dvSerialInfo)) {
        dvSerialInfo.detach().appendTo('body'); // 'body'
    }

    var dlgStartJob = $('#dlgStartJob');
    if (UIUtils.IsValid(dlgStartJob)) {
        dlgStartJob.detach().appendTo('body'); // 'body'
    }

    var dlgJobInst = $('#dlg_job_instruct_cnt');
    if (UIUtils.IsValid(dlgJobInst)) {
        dlgJobInst.detach().appendTo('body'); // 'body'
    }

    var dlgHoldJob = $('#dlgHoldJob');
    if (UIUtils.IsValid(dlgHoldJob)) {
        dlgHoldJob.detach().appendTo('body'); // 'body'
    }

    var dlgCloseJob = $('#dlgCloseJob');
    if (UIUtils.IsValid(dlgCloseJob)) {
        dlgCloseJob.detach().appendTo('body'); // 'body'
    }

    var dlgWOAttach = $('#dlgWOAttach');
    if (UIUtils.IsValid(dlgWOAttach)) {
        dlgWOAttach.detach().appendTo('body'); // 'body'
    }

    var dlgJobResults = $('#dlgJobResults');
    if (UIUtils.IsValid(dlgJobResults)) {
        dlgJobResults.detach().appendTo('body'); // 'body'
    }

    var dlgViewOperInst = $('#dlgViewOperInst');
    if (UIUtils.IsValid(dlgViewOperInst)) {
        dlgViewOperInst.detach().appendTo('body'); // 'body'
    }

    var dlgViewItemAttachments = $('#dlgViewItemAttachments');
    if (UIUtils.IsValid(dlgViewItemAttachments)) {
        dlgViewItemAttachments.detach().appendTo('body'); // 'body'
    }

    var dlgReschJob = $('#dlgReschJob');
    if (UIUtils.IsValid(dlgReschJob)) {
        dlgReschJob.detach().appendTo('body'); // 'body'
    }

    var dlg_wo_cls_atch_cnt = $('#dlg_wo_cls_atch_cnt');
    if (UIUtils.IsValid(dlg_wo_cls_atch_cnt)) {
        dlg_wo_cls_atch_cnt.detach().appendTo('body'); // 'body'
    }

    var dlg_wo_grd_msg_cnt = $('#dlg_wo_grd_msg_cnt');
    if (UIUtils.IsValid(dlg_wo_grd_msg_cnt)) {
        dlg_wo_grd_msg_cnt.detach().appendTo('body'); // 'body'
    }

    var dlgCJAddNotes = $('#dlgCJAddNotes');
    if (UIUtils.IsValid(dlgCJAddNotes)) {
        dlgCJAddNotes.detach().appendTo('body'); // 'body'
    }

    var dlg_print_rte_cnt = $('#dlg_print_rte_cnt');
    if (UIUtils.IsValid(dlg_print_rte_cnt)) {
        dlg_print_rte_cnt.detach().appendTo('body'); // 'body'
    }

    var dlg_wo_file_cnt = $('#dlg_wo_file_cnt');
    if (UIUtils.IsValid(dlg_wo_file_cnt)) {
        dlg_wo_file_cnt.detach().appendTo('body'); // 'body'
    }

    var dlg_bulk_prea = $('#dlgBulkMachPreAssign');
    if (UIUtils.IsValid(dlg_bulk_prea)) {
        dlg_bulk_prea.detach().appendTo('body'); // 'body'
    }
    
    var dlgSplitCard = $('#dlgSplitCard');
    if (UIUtils.IsValid(dlgSplitCard)) {
        dlgSplitCard.detach().appendTo('body'); // 'body'
    }

    var dlg_rfq_Notes = $('#dlg_rfq_Notes');
    if (UIUtils.IsValid(dlg_rfq_Notes)) {
        dlg_rfq_Notes.detach().appendTo('body');
    }

    var dlg_rfq_up_cnt = $('#dlg_rfq_up_cnt');
    if (UIUtils.IsValid(dlg_rfq_up_cnt)) {
        dlg_rfq_up_cnt.detach().appendTo('body');
    }

    var dlg_rfq_grd_msg_cnt = $('#dlg_rfq_grd_msg_cnt');
    if (UIUtils.IsValid(dlg_rfq_grd_msg_cnt)) {
        dlg_rfq_grd_msg_cnt.detach().appendTo('body');
    }

    //var dlgPayInv = $('#dlgPayInv');
    //if (UIUtils.IsValid(dlgPayInv)) {
    //    dlgPayInv.detach().appendTo('body'); // 'body'
    //}

    var dlgSupplierPieChart = $('#dlgSupplierPieChart');
    if (UIUtils.IsValid(dlgSupplierPieChart)) {
        dlgSupplierPieChart.detach().appendTo('body'); // 'body'
    }

    var dlgSupplierPieChartT = $('#dlgSupplierPieChartT');
    if (UIUtils.IsValid(dlgSupplierPieChartT)) {
        dlgSupplierPieChartT.detach().appendTo('body'); // 'body'
    }

    var dlgMonthSupplierChart = $('#dlgMonthSupplierChart');
    if (UIUtils.IsValid(dlgMonthSupplierChart)) {
        dlgMonthSupplierChart.detach().appendTo('body'); // 'body'
    }

    var dlgMonthSupplierChartT = $('#dlgMonthSupplierChartT');
    if (UIUtils.IsValid(dlgMonthSupplierChartT)) {
        dlgMonthSupplierChartT.detach().appendTo('body'); // 'body'
    }

    var dlgMonthPlantChart = $('#dlgMonthPlantChart');
    if (UIUtils.IsValid(dlgMonthPlantChart)) {
        dlgMonthPlantChart.detach().appendTo('body'); // 'body'
    }

    var dlgMonthPlantChartT = $('#dlgMonthPlantChartT');
    if (UIUtils.IsValid(dlgMonthPlantChartT)) {
        dlgMonthPlantChartT.detach().appendTo('body'); // 'body'
    }

    var dlgStockOutChart = $('#dlgStockOutChart');
    if (UIUtils.IsValid(dlgStockOutChart)) {
        dlgStockOutChart.detach().appendTo('body'); // 'body'
    }

    var dlgStockOutChartT = $('#dlgStockOutChartT');
    if (UIUtils.IsValid(dlgStockOutChartT)) {
        dlgStockOutChartT.detach().appendTo('body'); // 'body'
    }

    var dlgOnTimeShipmentChart = $('#dlgOnTimeShipmentChart');
    if (UIUtils.IsValid(dlgOnTimeShipmentChart)) {
        dlgOnTimeShipmentChart.detach().appendTo('body'); // 'body'
    }

    var dlgOnTimeShipmentChartT = $('#dlgOnTimeShipmentChartT');
    if (UIUtils.IsValid(dlgOnTimeShipmentChartT)) {
        dlgOnTimeShipmentChartT.detach().appendTo('body'); // 'body'
    }

    var dlg_ryg_grd_msg_cnt = $('#dlg_ryg_grd_msg_cnt');
    if (UIUtils.IsValid(dlg_ryg_grd_msg_cnt)) {
        dlg_ryg_grd_msg_cnt.detach().appendTo('body'); // 'body'
    }

    var dlg_ryg_grd_bom_cnt = $('#dlg_ryg_grd_bom_cnt');
    if (UIUtils.IsValid(dlg_ryg_grd_bom_cnt)) {
        dlg_ryg_grd_bom_cnt.detach().appendTo('body'); // 'body'
    }

    var current = $(window).scrollTop();
    $('body').scroll(function () {
        $('body').scrollTop(current);
    });

    $(".collapsible-div").ebocollapsiblediv();
}

function init_img_path() {
    image_ajaxLoading = '<img id=\"ajax-loader\" src=\"' + IMG_PATH + '/images/page/ajax-loader.gif\"/>';
    image_ajaxLoading2 = '<img id=\"ajax-loader2\" src=\"' + IMG_PATH + '/images2/imgbox/imgbox-spinner.gif\"/>';
    IPH_CONT_OFF_IMG = IMG_PATH + '/images2/iphonecheckbox/iphone_switch_container_off.png';
    IPH_CONT_ON_IMG = IMG_PATH + '/images2/iphonecheckbox/iphone_switch_container_on.png';
    IPH_SWITCH_IMG = IMG_PATH + '/images2/iphonecheckbox/iphone_switch.png';
    FANCY_ERR_IMG = IMG_PATH + '/images/Icons/Error.gif';
    image_Color_Picker_Url = IMG_PATH + '/images/Icons/color.png';
    DATEPICKER_PREV_URL = IMG_PATH + '/images/EboDatePicker/Prev.gif'
    DATEPICKER_NEXT_URL = IMG_PATH + '/images/EboDatePicker/Next.gif'
    TAB_OFF_IMG = IMG_PATH + '/images/TabPage/off.gif';
    TAB_ON_IMG = IMG_PATH + '/images/TabPage/on.gif'; 
}

function init_dtFormat(){
    switch(CUR_USR_DT_FORMAT){
        case "m/d/y":
            dtFormat = 0; // DATE_INPUT_FORMAT_MDY
            break;
        case "d/m/y":
        case "d-m-y":
        case "d.m.y":
            dtFormat = 1; // DATE_INPUT_FORMAT_DMY
            break;
        case "y-m-d":
            dtFormat = 2; // DATE_INPUT_FORMAT_YMD
            break;
    }
    ebo.dtFormat = dtFormat;
}

function jquery_Ready_Documnet() {
    init_img_path();
    init_dtFormat();

    $("#breadCrumb").jBreadCrumb({ easing: 'linear'});
    $(".menubarleft").lavaLamp({ fx: "backout", speed: 700 });
    
    InitPage();
    
    $(".ebodatepickerR").each(function() {
        $(this).attachEboDateHelper({ type: 'RANGE', declaredHolidays: hd, weeklyHolidays: whd });
    });

    $(".ebodatepickerS,.grddtctl").each(function () {
        var _oj = $(this), atAInit = _oj.attr("autoInit"), alhwd = _oj.attr("allowHolidays"), dtToday = new Date();
        _oj.attachEboDateHelper({ type: 'SIMPLE', declaredHolidays: hd, weeklyHolidays: whd,
            autoInit: (atAInit == "Y" || atAInit==undefined || atAInit==null),
            allowHolidays: (alhwd == "Y" || alhwd == undefined || alhwd == null),
            allowableMinFromDate: (alhwd == "N")? dtToday.setDate(dtToday.getDate() - 1) : null
        });
    });

    $(".ebodatepickerA").each(function() {
        $(this).attachEboDateHelper({ type: 'ALL', declaredHolidays: hd, weeklyHolidays: whd });
    });

    $(".imgbox").imgbox({ 'speedIn': 0, 'speedOut': 0, 'alignment': 'center', 'overlayShow': true, 'allowMultiple': false });
    $(".fancybox").fancybox({ 'zoomSpeedIn': 500, 'zoomSpeedOut': 500, 'overlayShow': true, 'overlayOpacity': 0.7, 'overlayColor': '#FFF', errorImgSrc: FANCY_ERR_IMG });

    $("#tpMenu").ebopopup({ popupchildElementID: "#tpMenuD", alignment: "bottom", topOffset: 18, halignment: "left",
        aftershow: function(obj) { obj.removeClass("switchbusunitout").addClass("switchbusunitover") },
        afterhide: function(obj) { obj.addClass("switchbusunitout").removeClass("switchbusunitover") }
    });
    
    $("#tpShortcuts").ebopopup({ popupchildElementID: "#tpShortcutsD", alignment: "bottom", topOffset: 18, halignment: "left",
        aftershow: function(obj) { obj.removeClass("switchbusunitout").addClass("switchbusunitover") },
        afterhide: function(obj) { obj.addClass("switchbusunitout").removeClass("switchbusunitover") } 
    });

    $("#tpFavoritesD").html($("#favorites").html());

    $("#tpFavorites").ebopopup({ popupchildElementID: "ul#tpFavoritesD", alignment: "bottom", topOffset: 18, halignment: "left",
        aftershow: function(obj) { obj.removeClass("switchbusunitout").addClass("switchbusunitover") },
        afterhide: function(obj) { obj.addClass("switchbusunitout").removeClass("switchbusunitover") } 
    });

    $('span.btn').keydown(function(e) {
        var code = e.which;
        // 13 = Enter button, 32 = Space
        if ((code === 13) || (code === 32)) {
            $(this).click();
            return false;
        }
    });
    init_Task_bar();
    init_filter_pnl_toggle();
    init_searchProvider();
}

function init_Task_bar() {
    var tlbrm = $("#Tbmenu");
    var tlbrm2 = $("#Tbsrchmenu");
    var imgArw = $(".arrow", tlbrm);
    var span_head_menu = $(".head_menu", tlbrm);
    var srch_menu = $("div#Tbsrchmenu");
    var srch_icon = $("img#imgTbCatSearch");
    var srch_cat_list = $("div#dvcat");
    var div_sub_menu = $(".sub_menu", tlbrm);
    var div_sub_menu2 = $(".sub_menu", tlbrm2);
    
    _TrapOtherClick1 = function(event) {
        var target = $(event.target);
        if (target.parents("#Tbmenu").length == 0) {
            span_head_menu.removeClass('active');
            div_sub_menu.hide();
            try {
                var src = (getTbImgSrc) ? getTbImgSrc(imgArw.attr('id'), '') : '';
            } catch (e) { }
            imgArw.attr('src', src);
        }
        else {
            // modified by Viswanath on 17-Apr-2015
            // when we added another menu 'Chatter'
            //click may be outside one menu but at the same time could be within another menu.
            var x = target.is(".head_menu");
            if (x) {
                submenu = target.parent().find(".sub_menu");
                div_sub_menu.not(submenu).hide();
                span_head_menu.not(target).removeClass('active');
            }
            
        }
    }


    //Modified by Viswanath for including Search category dropdown box
    _TrapOtherClick2 = function (event) {
        var target = $(event.target);
        if (target.parents("#Tbsrchmenu").length == 0) {
            div_sub_menu2.hide();
            try {
                var src = (getTbImgSrc) ? getTbImgSrc(imgArw.attr('id'), '') : '';
            } catch (e) { }
            imgArw.attr('src', src);
        }
    }

    $("#FFBgMax *[TbTip$='true']").tipsy({ gravity: 's' });

    span_head_menu.click(function () {
        $(this).removeClass('active');
        submenu = $(this).parent().find(".sub_menu");
        var top = -(submenu.height() + 22);
        var wdth = $(this).width();
        submenu.css({ top: top, left: "0px", width: wdth + 1})
        
        if (submenu.css('display') == "block") {
            $(this).removeClass("active");
            submenu.hide();
            $("img.arrow", $(this)).attr('src', getTbImgSrc($(this).attr('id'), 'hover'));
            $(document).unbind('click', _TrapOtherClick1)
        }
        else {
            $(this).addClass("active");
            submenu.fadeIn();
            $(".tipsy").remove()
            $(".arrow", $(this)).attr('src', getTbImgSrc($(".arrow", $(this)).attr('id'), ''));
            $(document).bind('click', _TrapOtherClick1)
        }

        $(".sub_menu:visible").not(submenu).hide();
        imgArw.not(this).attr('src', getTbImgSrc($(".arrow", $(this)).attr('id'), ''));

    });

    srch_icon.click(function () {
        submenu = $(this).parent().find(".sub_menu");
        var top = -(submenu.height() + 35);
        var wdth = submenu.width();
        submenu.css({ top: top, left: -5, width: wdth })
        if (submenu.css('display') == "block") {
            submenu.hide();
            $(document).unbind('click', _TrapOtherClick2)
        }
        else {
            $(this).addClass("active");
            submenu.fadeIn();
            $(".tipsy").remove()
            $(document).bind('click', _TrapOtherClick2)
        }
        $(".sub_menu:visible").not(submenu).hide();
    });

    imgArw.mouseover(function() { $(this).attr('src', getTbImgSrc($(this).attr('id'), 'hover')); })
    imgArw.mouseout(function() {
        if ($(this).parent().parent().find(".sub_menu").css('display') != "block") {
            $(this).attr('src', getTbImgSrc($(this).attr('id'), ''));
        } else {
            $(this).attr('src', getTbImgSrc($(this).attr('id'), ''));
        }
    });

    span_head_menu.mouseover(function() { $(this).addClass('over') }).mouseout(function() { $(this).removeClass('over') })
    div_sub_menu.mouseover(function() { $(this).fadeIn(); }).blur(function() { $(this).hide(); span_head_menu.removeClass('active'); })
}

function getTbImgSrc(id, type) {
    var src = "";
    switch (id) {
        case "imgTbAppSwitch":
        case "imgTbChatter":
        case "imgTbCatSearch":
            if (type == "hover")
                src = IMG_PATH + '/images/taskbar/app_hover.gif';
            else
                src = IMG_PATH + '/images/taskbar/app.gif';
            break;
       
    }
    return src;
}

function init_filter_pnl_toggle() {
    $("#ShowHideFilterArea").click(function() {
        $("#FilterAreaDetail").toggle()
        if ($("#FilterAreaDetail").is(":visible")) {
            $(this).html("Hide Filter")
        }
        else {
            $(this).html("Show Filter")
        }
    });
}

function do_Master_Resize() {
    $(".mainBg").css({ width: window.screen.width - 30 })
    $(".main").css({ width: window.screen.width - 48 })
}

function RemoveLastChar(str, strChar) {
    var strRtn = str;
    if (str.charAt(str.length - 1) == "|") {
        strRtn = str.substring(0, str.length - 1);
    }
    return strRtn;
}

function _doFdwnLd(url, pms, shM) {
    if (arguments.length < 3) shM = "0";
    var strFeatures = "outerHeight=5,innerHeight=300,Height=420,Width=470,"
        + "toolbar=0,location=0,status=0,menubar=" + shM + ","
        + "directories=0,scrollbars=1,resizable=1,top=" + (window.innerHeight - 400) / 2
        + ",left=" + (window.innerWidth - 400) / 2;

    url = ((pms == "" || pms == undefined) ? url : ((url.indexOf("?") > -1) ? (url + "&" + pms) : (url + '?' + pms)))
    var wndW = window.open(url , "winDownLoad", strFeatures, false);
    return wndW;
}

function _doWinCEScan(url, pms) {
    var strFeatures = "outerHeight=5,innerHeight=300,Height=300,Width=230,toolbar=0,location=0,status=0,menubar=0,"
        + "directories=0,scrollbars=1,resizable=0,top=0,left=0";
    window.open(url + "?" + pms, "winDownLoad", strFeatures, false);
}

function _vWItemSpec(n, v) {
    if (ITEM_SPEC_URL=="") return;
    _doFdwnLd(ITEM_SPEC_URL, $.format("{0}={1}", n, v));
}
/*info bar*/
var _info_br = null;
function info_br_shw(msg, oncls) {
    if (_info_br == null) {
        _info_br = $("#t_info_br");
        $("#t_info_br_cls", _info_br).click(function() { info_br_cls(); return false; });
    }
    if (!_info_br.is(":visible")) {
        _info_br.slideDown(400);
        $("#t_info_br_cls", _info_br).unbind('click').click(function() { if (oncls) oncls(); info_br_cls(); return false; });
    }
    $("#t_info_br_cont", _info_br).html(msg);
}
function info_br_cls() { if (_info_br != null && _info_br.is(":visible")) _info_br.fadeOut(400); }

//-----Start----Keep Alive Timer----------
var _t_out_s = 0, _t_out_tmr=null;
function _farwctdwn(s) {
    s = parseInt(s, 10); _t_out_s = (isNaN(s) || s <= 0) ? parseInt(1200, 10) : s;
    _clear_t_out_tmr(); _t_out_tmr = window.setInterval(_factdwn, 1000);
}
function _clear_t_out_tmr() { info_br_cls(); window.clearInterval(_t_out_tmr); }
function _factdwn() {
    if (_t_out_s <= 0) {
        _clear_t_out_tmr();
        info_br_shw(SESS_EXP_MSG, _clear_t_out_tmr);
        var hrefpage = document.location.href;
        goPage(hrefpage, "rbusgid=" + redir_bgid + "&rapp=" + redir_app + "&rfeature=" + redir_feature);
    }
    else if (_t_out_s <= 60) { info_br_shw($.format(SESS_WRN_MSG, _t_out_s, "<a href='javascript:_rwfatkt();'>", "</a>"), _clear_t_out_tmr); }
    _t_out_s -= 1;
}

function _rwfatkt(bReload) {
    if (arguments.length == 0) bReload = true;
    _clear_t_out_tmr();
    $.ajax({ type: "POST", url: RENEW_FA_TICKET_URL, data: { "r": "y" }, dataType: "json",
        success: function(data) { _farwctdwn(data.expires); }, cache: false,
        error: function(xhr, status, err) { if (bReload) { document.location.href = document.location.href; } }
    });
}

function _ajax_ls_rwfatkt() {
    try { _rwfatkt(false); } catch (e) {}
}

//-------End --Keep Alive Timer----------
//uses Encoder from ebo_other_ui_1.js
function HTMLEncode(s) { Encoder.EncodeType = "entity"; var o = Encoder.htmlEncode(s, false); return o; }
function cs_shwAjaxErr(xhr, errTxt, err) {
    if ($.trim(xhr.responseText) != "") { shwLdDiag('INFO', xhr.responseText); } else { shwLdDiag('INFO', errTxt); }
}

function getEntityData(pageUrl, pltgid, entType, options) {
    var defaultOptions = {
        type: 'GET',
        url: pageUrl,
        dataType: 'json',
        data: { plantgid: pltgid, enttype: entType },
        async: false,
        error: function (xhr, errTxt, err) { cs_shwAjaxErr(xhr, errTxt, err) },
        success: function (data) { }
    };
    defaultOptions = $.extend({}, defaultOptions, options);
    $.ajax(defaultOptions);
}
// Supplier StAatus, Queue
function getEntityDropdownList(DDPageURL,pltgid, entType, entValue, filterCtrlName, divContainerID, additionlFilterString, onSuccessCallBack, style) {
    additionlFilterString = additionlFilterString == null ? '' : additionlFilterString;
    var localStyle = UIUtils.IsValid(style) ? style : 'width: 100px';
    $.ajax({
        type: 'GET',
        url: DDPageURL,
        dataType: 'json',
        data: { plantgid: pltgid, enttype: entType, entvalue: entValue, additionalFilter: additionlFilterString  },
        async: false,
        error: function(xhr, errTxt, err) { cs_shwAjaxErr(xhr, errTxt, err) },
        success: function (data) {
            if ($.isFunction(onSuccessCallBack)) {
                onSuccessCallBack(data);
            } else {
                var htm = "";
                htm = "<select Class='dropdown' name='" + filterCtrlName + "' id='" + filterCtrlName + "' style='" + localStyle + "'>";
                for (var elem in data) {
                    GID = HtmlDecode(elem);
                    text = data[elem][0];
                    if (entValue == GID || (entValue == '$' && GID == '&#36;')) {

                        htm += "<option value='" + GID + "' selected  >" + text + "</option>";
                    }
                    else {
                        htm += "<option value='" + GID + "' >" + text + "</option>";
                    }
                }
                htm += "</select>";
                $("div#" + divContainerID).html(htm);
            }
        }
    });
}

function getEntityDropdownList4Supplier(DDPageURL, suppliergid, entType, entValue, filterCtrlName, divContainerID, style) {
    var localStyle = UIUtils.IsValid(style) ? style : 'width: 100px';
    $.ajax({
        type: 'GET',
        url: DDPageURL,
        dataType: 'json',
        data: { suppliergid: suppliergid, enttype: entType, entvalue: entValue },
        async: false,
        success: function(data) {
            var htm = "";
            htm = "<select Class='dropdown' name='" + filterCtrlName + "' id='" + filterCtrlName + "' style='" + localStyle + "'>";
            for (var elem in data) {
                GID = HtmlDecode(elem);
                text = data[elem][0];
                if (entValue == GID || (entValue == '$' && GID == '&#36;')) {

                    htm += "<option value='" + GID + "' selected  >" + text + "</option>";
                }
                else {
                    htm += "<option value='" + GID + "' >" + text + "</option>";
                }
            }
            htm += "</select>";
            $("div#" + divContainerID).html(htm);

        }
    });
}

function getEntityDropdownList4PlantSupplier(DDPageURL, plantgid, suppliergid, entType, entValue, filterCtrlName, divContainerID, style) {
    var localStyle = UIUtils.IsValid(style) ? style : 'width: 100px';
    $.ajax({
        type: 'GET',
        url: DDPageURL,
        dataType: 'json',
        data: { plantgid: plantgid, suppliergid: suppliergid, enttype: entType, entvalue: entValue },
        async: false,

        success: function(data) {
            var htm = "";
            htm = "<select Class='dropdown' name='" + filterCtrlName + "' id='" + filterCtrlName + "' style='" + localStyle + "'>";
            for (var elem in data) {
                GID = HtmlDecode(elem);
                text = data[elem][0];
                if (entValue == GID || (entValue == '$' && GID == '&#36;')) {

                    htm += "<option value='" + GID + "' selected  >" + text + "</option>";
                }
                else {
                    htm += "<option value='" + GID + "' >" + text + "</option>";
                }
            }
            htm += "</select>";
            $("div#" + divContainerID).html(htm);

        }
    });
}


// A small utilty for converting html special characters into equvalent string values
// Basically a div element is created in memory, but it is never appended to the document.
function HtmlDecode(spl) {
    return $('<div/>').html(spl).text(); 
}

function clone(obj) {
    var len = 0;
    var copy;
    if (obj == null || typeof obj != "object") return obj;
    // Handle Date 
    if (obj instanceof Date) {
        copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }
    // Handle Array 
    if (obj instanceof Array) {
        len = obj.length;
        copy = [];
        for (var i = 0; i < len; ++i) {
            copy[i] = clone(obj[i]);
        }
        return copy;
    }
    // Handle Object 
    if (obj instanceof Object) {
        copy = {};
        for (var attr in obj) {
            if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
        }
        return copy;
    }
    return null;
}


String.prototype.formatfirst = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
        return (typeof args[number] != 'undefined') ? args[number] : match;
    });
};

String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{' + i + '\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
}; 


/**
 * Extracts the browser name and version number from user agent string.
 *
 * @param userAgent
 *            The user agent string to parse. If not specified, the contents of
 *            navigator.userAgent are parsed.
 * @param elements
 *            How many elements of the version number should be returned. A
 *            value of 0 means the whole version. If not specified, defaults to
 *            2 (major and minor release number).
 * @return A string containing the browser name and version number, or null if
 *         the user agent string is unknown.
 */
function identifyBrowser(userAgent, elements) {
    var regexps = {
        'Chrome': [/Chrome\/(\S+)/],
        'Firefox': [/Firefox\/(\S+)/],
        'MSIE': [/MSIE (\S+);/],
        'MSIE11': [/Trident\/(\S+);/],
        'Opera': [
            /Opera\/.*?Version\/(\S+)/,     /* Opera 10 */
            /Opera\/(\S+)/                  /* Opera 9 and older */
        ],
        'Safari': [/Version\/(\S+).*?Safari\//]
    },
        re, m, browser, version;

    if (userAgent === undefined)
        userAgent = navigator.userAgent;

    if (elements === undefined)
        elements = 2;
    else if (elements === 0)
        elements = 1337;

    for (browser in regexps)
        while (re = regexps[browser].shift())
            if (m = userAgent.match(re)) {
                version = (m[1].match(new RegExp('[^.]+(?:\.[^.]+){0,' + --elements + '}')))[0];
                return browser + ' ' + version;
            }

    return null;
}
var _tskbar_frm_posted = false;
function _tskbar_dosrch() {
    if (_tskbar_frm_posted) return;
    var txt = $("#txtTbSearch");
    if ($.trim(txt.val()) == "" || txt.val() == txt.attr("defV") || $.trim(txt.val()).length < parseInt(txt.attr("minlength"))) {
        var errText = "<div class=\'invalid-search-modal-content\'>Please enter a valid search value.<br /><br />Minimum length: " + txt.attr("minlength") + " characters </div>";

        var options = {
            modalType: 'Close',
            closeButtonText: 'Ok',
            needCloseConfirm: false,
            modalId: 'modal-invalid-search-bu',
            modalText: errText,
        };
        showModal(options);
        return false;
    }
    _tskbar_frm_posted = true;
    return true;

}
function _tskbar_onkeypress(o, e) {
    if (e.keyCode == 13 || e.which == 13) {
        return false;
    }
}



function removeDefaultValue(obj) {
    var thisValue = obj.value;
    if (thisValue == $(obj).attr("defaultvalue")) {
        obj.value = "";
    }
    return true;
}

function _doAjax (url, data, onsucsess, rtnType, onerror) {
    if (arguments.length < 4) rtnType = "json";
    if (arguments.length < 5) onerror = curObj.ajaxError;
    data.fm = "dsh"; //add this for all ajax request
    var request = $.ajax({
        type: "POST", url: url, data: data, dataType: rtnType,
        error: onerror, success: onsucsess, cache: false,
        statusCode: curObj.handleAjaxStatus
    });

    request.done(function (d, msg, jqXHR) {
        curObj.console.log("ajax request: " + url + " done: " + d);
    });
    request.fail(function (jqXHR, textStatus) {
        curObj.console.log("ajax request: " + url + " failed: " + textStatus);
    });
    request.always(function (d, msg, jqXHR) {
        curObj.console.log("ajax request : " + url + " completed with msg " + msg);
        curObj.console.log(jqXHR.responseText);
    });
}

function _convertToNumber(v) {
    if (IsCommaAsDecimalSep) {
        v = (v.toString()).replace(/\./g, "").replace(/,/g, '.');
    }
    return parseFloat(v);
}

function m_getSearchProviders() {
    var osrchchk = $("input:checkbox", $("div#dvcat"));
    var srchval = "";
    osrchchk.each(function () {
        var $this = $(this);
        var val = $this.val();
        if ($this.is(':checked')) { // daniel.tenorio - using jquery way to know if checkbox is checked.
            if (val == "All") {
                return "";
            }
            else {
                srchval = (srchval == "") ? val : srchval + "," + val;
            }
        }
    });
    return srchval;
}

function init_searchProvider() {
    var osrchchk = $("input:checkbox", $("div#dvcat"));
    osrchchk.click(function () {
        var chk = $(this), val = chk.val();
        if (val == "All") {
            if (chk.is(':checked')) {
                osrchchk.attr("checked", "checked");
            }
            else {
                osrchchk.removeAttr("checked");
            }
        }
        var ohdnProviders = $("input:hidden[name$='SearchProviders']");
        ohdnProviders.val(m_getSearchProviders());
    });
}

function roundTo(n, digits) {
    if (digits === undefined) {
        digits = 0;
    }

    var multiplicator = Math.pow(10, digits);
    n = parseFloat((n * multiplicator).toFixed(11));
    return Math.round(n) / multiplicator;
}

function ToggleHomeFilter() {
    var container = $('div.collapsible-filter-btn-container');
    var filterContainer = $('div.filter-section-container');

    if (UIUtils.IsValid(container) && UIUtils.IsValid(filterContainer)) {
        if (container.hasClass('pressed')) {
            container.removeClass('pressed');
            filterContainer.addClass('hide-filter');
        } else {
            container.addClass('pressed');

            var layoutContainer = $('div.ui-layout-section-container');
            if (!layoutContainer.hasClass('hide-filter'))
                ToggleHomeLayoutSettings();

            filterContainer.removeClass('hide-filter');
        }
    }
}

function ToggleHomeLayoutSettings() {
    var container = $('div.collapsible-ui-layout-btn-container');
    var layoutContainer = $('div.ui-layout-section-container');

    if (UIUtils.IsValid(container) && UIUtils.IsValid(layoutContainer)) {
        if (container.hasClass('pressed')) {
            container.removeClass('pressed');
            layoutContainer.addClass('hide-filter');
            $("div.content").css('height', $("div.content").height() + 55);
        } else {
            container.addClass('pressed');

            var filterContainer = $('div.filter-section-container');
            if (!filterContainer.hasClass('hide-filter'))
                ToggleHomeFilter();

            layoutContainer.removeClass('hide-filter');

            $("div.content").css('height', $("div.content").height() - 43);
        }
    }
}

function EditUILayout(event) {
    var editBtnContainer = $('.btn-edit-layout-filter-section');
    var saveBtnContainer = $('.btn-save-layout-filter-section');
    var cancelBtnContainer = $('.btn-cancel-layout-filter-section');

    editBtnContainer.removeClass('showElementInline');
    editBtnContainer.addClass('hideElement');
    saveBtnContainer.removeClass('hideElement');
    saveBtnContainer.addClass('showElementInline');
    cancelBtnContainer.removeClass('hideElement');
    cancelBtnContainer.addClass('showElementInline');

    var gridStackObj = HomeHelper.GetHomeGridStackObj();
    gridStackObj.movable('.grid-stack-item', true);

    HomeHelper.AddRemoveHomePanelMovableCursor(true);
    TriggerGritterNotification(
        {
            type: 'info',
            title: ult_locale.HOME_MSG_1,
            text: ult_locale.HOME_MSG_3
        });
}

function SaveUILayout(event) {
    var editBtnContainer = $('.btn-edit-layout-filter-section');
    var saveBtnContainer = $('.btn-save-layout-filter-section');
    var cancelBtnContainer = $('.btn-cancel-layout-filter-section');

    editBtnContainer.removeClass('hideElement');
    editBtnContainer.addClass('showElementInline');
    saveBtnContainer.removeClass('showElementInline');
    saveBtnContainer.addClass('hideElement');
    cancelBtnContainer.removeClass('showElementInline');
    cancelBtnContainer.addClass('hideElement');

    ToggleHomeLayoutSettings();

    HomeHelper.SavePanelDim(false);
}

function ResetUILayout(event) {
    var editBtnContainer = $('.btn-edit-layout-filter-section');
    var saveBtnContainer = $('.btn-save-layout-filter-section');
    var cancelBtnContainer = $('.btn-cancel-layout-filter-section');

    editBtnContainer.removeClass('hideElement');
    editBtnContainer.addClass('showElementInline');
    saveBtnContainer.removeClass('showElementInline');
    saveBtnContainer.addClass('hideElement');
    cancelBtnContainer.removeClass('showElementInline');
    cancelBtnContainer.addClass('hideElement');

    ToggleHomeLayoutSettings();

    HomeHelper.ResetPanelDim();
}

function CancelUILayout(event) {
    var editBtnContainer = $('.btn-edit-layout-filter-section');
    var saveBtnContainer = $('.btn-save-layout-filter-section');
    var cancelBtnContainer = $('.btn-cancel-layout-filter-section');

    editBtnContainer.removeClass('hideElement');
    editBtnContainer.addClass('showElementInline');
    saveBtnContainer.removeClass('showElementInline');
    saveBtnContainer.addClass('hideElement');
    cancelBtnContainer.removeClass('showElementInline');
    cancelBtnContainer.addClass('hideElement');

    var gridStackObj = HomeHelper.GetHomeGridStackObj();
    gridStackObj.movable('.grid-stack-item', false);

    HomeHelper.AddRemoveHomePanelMovableCursor(false);

    ToggleHomeLayoutSettings();

    TriggerGritterNotification(
        {
            type: 'info',
            title: ult_locale.HOME_MSG_2,
            text: ult_locale.HOME_MSG_4
        });
}

function TriggerGritterNotification(opts) {
    var INFO_TYPE = 'info';
    var INFO_IMAGE = '../Content/images/Gritter/info-large.png';
    var WARNING_TYPE = 'warning';
    var WARNING_IMAGE = '../Content/images/Gritter/warning-large.png';
    var SUCCESS_TYPE = 'success';
    var SUCCESS_IMAGE = '../Content/images/Gritter/success-large.png';
    var ERROR_TYPE = 'error';
    var ERROR_IMAGE = '../Content/images/Gritter/error-large.png';

    opts = $.extend({
        'type': INFO_TYPE,
        "title": '',
        "text": '',
        'time': 8000,
        "sticky": false
    }, opts || {});

    var selImage = INFO_IMAGE;
    switch (opts.type) {
        case INFO_TYPE:
            selImage = INFO_IMAGE;
            break;
        case WARNING_TYPE:
            selImage = WARNING_IMAGE;
            break;
        case SUCCESS_TYPE:
            selImage = SUCCESS_IMAGE;
            break;
        case ERROR_TYPE:
            selImage = ERROR_IMAGE;
            break;
    }

    return $.gritter.add({ title: opts.title, text: opts.text, image: selImage, sticky: opts.sticky });
}

// Adding this polyfill to support isInteger in IE browsers (Not using ES6)
Number.isInteger = Number.isInteger || function (value) {
    return typeof value === "number" &&
        isFinite(value) &&
        Math.floor(value) === value;
};

(function ($) {
    $.fn.hasScrollBar = function () {
        return this.get(0).scrollHeight > this.height();
    }
})(jQuery);


// JQuery 3.5.1 deprecated size function and forced users to use length.
// Doing this our gridstack library will be able to use size without any error.
(function ($) {
    $.fn.extend({
        size: function () {
            return $(this).length;
        }
    });
})(jQuery);


function onIntegrationDropdownClick(event, defaultValue) {
    var wrapper = $(event.target);
    var ddw = wrapper.closest('div.report-dropdown-container2').find('div#' + wrapper.closest('span.ui-dropdownchecklist-selector-wrapper').attr('id') + '-ddw');
    var allCheck = ddw.find('input[type="checkbox"][value="' + defaultValue + '"]');
    if (UIUtils.IsValid(allCheck)) {
        if (allCheck.is(':checked')) {
            var checkboxes = ddw.find(('input[type="checkbox"][value!="' + defaultValue + '"]'));
            if (UIUtils.IsValid(checkboxes)) {
                checkboxes.each(function () {
                    var checkboxElem = $(this);
                    checkboxElem.prop('checked', false);
                    checkboxElem.attr('disabled', 'disabled');
                    checkboxElem.closest('div.ui-dropdownchecklist-item').addClass('ui-state-disabled');
                });
            }
        }
    }
}

function onIntegrationDropdownCheckClick(checkboxInp, defaultValue) {
    if (checkboxInp.val() === defaultValue) {
        var checkboxes = checkboxInp.closest('div.ui-dropdownchecklist-dropcontainer').find('input[type="checkbox"][value!="' + defaultValue + '"]');
        if (UIUtils.IsValid(checkboxes)) {
            if (checkboxInp.is(':checked')) {
                checkboxes.each(function () {
                    var checkboxElem = $(this);
                    checkboxElem.prop('checked', false);
                    checkboxElem.attr('disabled', 'disabled');
                    checkboxElem.closest('div.ui-dropdownchecklist-item').addClass('ui-state-disabled');
                });

                var textOptions = checkboxInp.closest('div.report-dropdown-container2').find('span.ui-dropdownchecklist-text');
                if (UIUtils.IsValid(textOptions)) {
                    textOptions.attr('title', checkboxInp.attr('chktxt'));
                    textOptions.html(checkboxInp.attr('chktxt'));
                }
            }
            else {
                checkboxes.each(function () {
                    var checkboxElem = $(this);
                    checkboxElem.prop('checked', false);
                    checkboxElem.removeAttr('disabled')
                    checkboxElem.closest('div.ui-dropdownchecklist-item').removeClass('ui-state-disabled');
                });
            }
        }
    }
}

function onIntegrationStatusClick(event) {
    onIntegrationDropdownClick(event, '');
}

function onIntegrationStatusCheckClick(checkboxInp) {
    onIntegrationDropdownCheckClick(checkboxInp, '');
}

function onIntegrationTypeClick(event) {
    onIntegrationDropdownClick(event, 'All');
}

function onIntegrationTypeCheckClick(checkboxInp) {
    onIntegrationDropdownCheckClick(checkboxInp, 'All');
}