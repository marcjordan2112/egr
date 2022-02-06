-- This addon was hacked up from SnapShot, LootLog, & AdvancedLootLog, and https://github.com/Baertram/ESO-ConstantsDumper
EsoGrinder = {}
EsoGrinder.name = "EsoGrinder"

EsoGrinder.ddebug = true
EsoGrinder.ddebug_in_function = true
EsoGrinder.started = true
EsoGrinder.version = "x"
EsoGrinder.version_eso_api = GetAPIVersion()
EsoGrinder.function_call_count = 0

function EsoGrinder.Print(msg)
    local z = zo_strformat ( "EGR <<1>>", msg)
    d(z)
end

function EsoGrinder.DebugPrintInFunction(msg)
    EsoGrinder.function_call_count = EsoGrinder.function_call_count + 1
    if EsoGrinder.ddebug_in_function then
        EsoGrinder.Print(zo_strformat("--> <<1>> <<2>>", EsoGrinder.function_call_count, msg))
        return
    end
end

function EsoGrinder.DebugPrint(msg)
    if EsoGrinder.ddebug then
        EsoGrinder.Print(msg)
        return
    end
end

function EsoGrinder.RegisterForAllEvents(extra)
    EsoGrinder.DebugPrintInFunction("RegisterForAllEvents")

    EVENT_MANAGER:RegisterForEvent(EsoGrinder.name,EVENT_LOOT_RECEIVED,EsoGrinder.EventLootReceivedHandler)
    EVENT_MANAGER:RegisterForEvent(EsoGrinder.name,EVENT_INVENTORY_SINGLE_SLOT_UPDATE,EsoGrinder.EventInventorySingleSlotUpdateHandler)
    EVENT_MANAGER:RegisterForEvent(EsoGrinder.name,EVENT_MONEY_UPDATE,EsoGrinder.EventMoneyUpdateHandler)
    EVENT_MANAGER:RegisterForEvent(EsoGrinder.name,EVENT_CURRENCY_UPDATE,EsoGrinder.EventCurrencyUpdateHandler)
end

function EsoGrinder.UnregisterAllEvents(extra)
    EsoGrinder.DebugPrintInFunction("UnregisterAllEvents")

    EVENT_MANAGER:UnregisterForEvent(EsoGrinder.name, EVENT_LOOT_RECEIVED)
    EVENT_MANAGER:UnregisterForEvent(EsoGrinder.name, EVENT_INVENTORY_SINGLE_SLOT_UPDATE)
    EVENT_MANAGER:UnregisterForEvent(EsoGrinder.name, EVENT_MONEY_UPDATE)
    EVENT_MANAGER:UnregisterForEvent(EsoGrinder.name, EVENT_CURRENCY_UPDATE)
end

function EsoGrinder.OnSlashCommandDebug(extra)
    EsoGrinder.DebugPrintInFunction("OnSlashCommandDebug")

    if EsoGrinder.ddebug then
        EsoGrinder.ddebug = false
        EsoGrinder.Print("Debug is now off.")
        return
    end

    EsoGrinder.ddebug = true
    EsoGrinder.Print("Debug is now on.")
end

function EsoGrinder.OnSlashCommandStart(extra)
    EsoGrinder.DebugPrintInFunction("OnSlashCommandStart")

    if EsoGrinder.started then
        EsoGrinder.DebugPrint("Already started.")
        return
    end

    EsoGrinder.RegisterForAllEvents()
    EsoGrinder.started = true
    EsoGrinder.DebugPrint("Started.")
end

function EsoGrinder.OnSlashCommandStop(extra)
    EsoGrinder.DebugPrintInFunction("OnSlashCommandStop")

    if not EsoGrinder.started then
        EsoGrinder.DebugPrint("Not started.")
        return
    end

    EsoGrinder.UnregisterAllEvents()
    EsoGrinder.started = false
    EsoGrinder.DebugPrint("Stopped.")
end

function EsoGrinder.OnSlashCommandVersion(extra)
    EsoGrinder.DebugPrintInFunction("OnSlashCommandVersion")

    EsoGrinder.Print(zo_strformat ( "Version = <<1>>", EsoGrinder.version))
    EsoGrinder.Print(zo_strformat ( "ESO API Version =  <<1>>", EsoGrinder.version_eso_api))
end

SLASH_COMMANDS["/egrdebug"] = EsoGrinder.OnSlashCommandDebug
SLASH_COMMANDS["/egrstart"] = EsoGrinder.OnSlashCommandStart
SLASH_COMMANDS["/egrstop"] = EsoGrinder.OnSlashCommandStop
SLASH_COMMANDS["/egrversion"] = EsoGrinder.OnSlashCommandVersion

function EsoGrinder.EventLootReceivedHandler(eventCode, lootedBy, itemLink, quantity, itemSound, lootType, isStolen)
    EsoGrinder.DebugPrintInFunction("EventLootReceivedHandler")

    local loot_type = lootType
    local use_ecl = false

    if use_ecl then
        EsoGrinder.DebugPrint ( "Using esoui_constants_live.lua functions." )
        -- currency_type = LootType_get_string(lootType)
    end

    local z = zo_strformat ( "eventCode=<<1>>, lootedBy=<<2>>, itemLink=<<3>>, quantity=<<4>>, itemSound=<<5>>,",
            eventCode,
            lootedBy,
            itemLink,
            quantity,
            itemSound)

    local z2 = zo_strformat ( "<<1>> lootType=<<2>>=<<3>>, isStolen=<<4>>",
            z,
            lootType,
            loot_type,
            isStolen)

    EsoGrinder.DebugPrint(z2)
end

function EsoGrinder.EventInventorySingleSlotUpdateHandler(eventCode, badId, slotIndex, isNewItem, itemSoundCategory, inventoryUpdateReason, stackCountChange)
    EsoGrinder.DebugPrintInFunction("EventInventorySingleSlotUpdateHandler")

    local use_ecl = false

    if use_ecl then
        EsoGrinder.DebugPrint ( "Using esoui_constants_live.lua functions." )
    end

    local z = zo_strformat ( "eventCode=<<1>>, bagId=<<2>>, slotIndex=<<3>>, isNewItem=<<4>>, itemSoundCategory=<<5>>,",
            eventCode,
            badId,
            slotIndex,
            isNewItem,
            itemSoundCategory)

    local z2 = zo_strformat ( "<<1>> inventoryUpdateReason=<<2>>, stackCountChange=<<3>>",
            z,
            inventoryUpdateReason,
            stackCountChange)

    EsoGrinder.DebugPrint(z2)
end

function EsoGrinder.EventMoneyUpdateHandler(newMoney, oldMoney, thisReason)
    EsoGrinder.DebugPrintInFunction("EventMoneyUpdateHandler")

    local delta_amount = oldMoney - newMoney
    local reason = thisReason
    local use_ecl = false

    if use_ecl then
        EsoGrinder.DebugPrint ( "Using esoui_constants_live.lua functions." )
    end

    local z = zo_strformat ( "newMoney=<<1>>, oldMoney=<<2>>, thisReason=<<3>>=<<4>>, delta_amount=<<5>>",
            newMoney,
            oldMoney,
            thisReason,
            reason,
            delta_amount)

    EsoGrinder.DebugPrint(z)
end

function EsoGrinder.EventCurrencyUpdateHandler(eventCode, currencyType, currencyLocation, newAmount, oldAmount, thisReason )
    EsoGrinder.DebugPrintInFunction("EventCurrencyUpdateHandler")

    local delta_amount = oldAmount - newAmount
    local currency_type = currencyType
    local currency_location = currencyLocation
    local reason = thisReason
    local use_ecl = false

    if use_ecl then
        EsoGrinder.DebugPrint ( "Using esoui_constants_live.lua functions." )
        currency_type = CurrencyType_get_string(currencyType)
        currency_location = CurrencyLocation_get_string(currencyLocation)
        reason = CurrencyChangeReason_get_string(thisReason)
    end

    local z = zo_strformat ( "eventCode=<<1>>, currencyType=<<2>>=<<3>>, currencyLocation=<<4>>=<<5>>,",
            eventCode,
            currencyType,
            currency_type,
            currencyLocation,
            currency_location)

    local z2 = zo_strformat ( "<<1>> reason=<<2>>=<<3>>, newAmount=<<4>>, oldAmount=<<5>>, delta_amount=<<6>>",
            z,
            thisReason,
            reason,
            newAmount,
            oldAmount,
            delta_amount)

    EsoGrinder.DebugPrint(z2)
end

function EsoGrinder.Initialize()
    EsoGrinder.ddebug = true
    EsoGrinder.ddebug_in_function = true
    EsoGrinder.DebugPrintInFunction("Initialize")

    EsoGrinder.RegisterForAllEvents()
end

function EsoGrinder.DelayedStartedMessage()
    EsoGrinder.DebugPrintInFunction("DelayedStartedMessage")

    EsoGrinder.Print("Started.")
end

function EsoGrinder.OnAddOnLoaded(event, addonName)
    EsoGrinder.function_call_count = 0
    EsoGrinder.DebugPrintInFunction(zo_strformat("OnAddOnLoaded (<<1>>)", addonName))

    if addonName == EsoGrinder.name then
        EsoGrinder.Initialize()
        EVENT_MANAGER:UnregisterForEvent(EsoGrinder.name,EVENT_ADD_ON_LOADED)
        zo_callLater(EsoGrinder.DelayedStartedMessage, 1000)
    end
end

EVENT_MANAGER:RegisterForEvent(EsoGrinder.name, EVENT_ADD_ON_LOADED, EsoGrinder.OnAddOnLoaded)
