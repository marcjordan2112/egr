-- This addon was hacked up from SnapShot, LootLog, & AdvancedLootLog, and https://github.com/Baertram/ESO-ConstantsDumper
EsoGrinderWip = {}
EsoGrinderWip.name = "EsoGrinderWip"

EsoGrinderWip.ddebug = false
EsoGrinderWip.ddebug_in_function = true
EsoGrinderWip.started = true
EsoGrinderWip.version = "3.0.0"
EsoGrinderWip.version_eso_api = GetAPIVersion()
EsoGrinderWip.function_call_count = 0

function EsoGrinderWip.Print(msg)
    z = zo_strformat ( "EGRW <<1>>", msg)
    d(z)
end

function EsoGrinderWip.DebugPrintInFunction(msg)
    EsoGrinderWip.function_call_count = EsoGrinderWip.function_call_count + 1
    if EsoGrinderWip.ddebug_in_function then
        EsoGrinderWip.Print(zo_strformat("--> <<1>> <<2>>", EsoGrinderWip.function_call_count, msg))
        return
    end
end

function EsoGrinderWip.DebugPrint(msg)
    if EsoGrinderWip.ddebug then
        EsoGrinderWip.Print(msg)
        return
    end
end

function EsoGrinderWip.RegisterForAllEvents(extra)
    EsoGrinderWip.DebugPrintInFunction("RegisterForAllEvents")

    EVENT_MANAGER:RegisterForEvent(EsoGrinderWip.name,EVENT_CURRENCY_UPDATE,EsoGrinderWip.EventCurrencyUpdateHandler)
end

function EsoGrinderWip.UnregisterAllEvents(extra)
    EsoGrinderWip.DebugPrintInFunction("UnregisterAllEvents")

    EVENT_MANAGER:UnregisterForEvent(EsoGrinderWip.name, EVENT_CURRENCY_UPDATE)
end

function EsoGrinderWip.OnSlashCommandDebug(extra)
    EsoGrinderWip.DebugPrintInFunction("OnSlashCommandDebug")

    if EsoGrinderWip.ddebug then
        EsoGrinderWip.ddebug = false
        EsoGrinderWip.Print("Debug is now off.")
        return
    end

    EsoGrinderWip.ddebug = true
    EsoGrinderWip.Print("Debug is now on.")
end

function EsoGrinderWip.OnSlashCommandStart(extra)
    EsoGrinderWip.DebugPrintInFunction("OnSlashCommandStart")

    if EsoGrinderWip.started then
        EsoGrinderWip.DebugPrint("Already started.")
        return
    end

    EsoGrinderWip.RegisterForAllEvents()
    EsoGrinderWip.started = true
    EsoGrinderWip.DebugPrint("Started.")
end

function EsoGrinderWip.OnSlashCommandStop(extra)
    EsoGrinderWip.DebugPrintInFunction("OnSlashCommandStop")

    if not EsoGrinderWip.started then
        EsoGrinderWip.DebugPrint("Not started.")
        return
    end

    EsoGrinderWip.UnregisterAllEvents()
    EsoGrinderWip.started = false
    EsoGrinderWip.DebugPrint("Stopped.")
end

function EsoGrinderWip.OnSlashCommandVersion(extra)
    EsoGrinderWip.DebugPrintInFunction("OnSlashCommandVersion")

    EsoGrinderWip.Print(zo_strformat ( "Version = <<1>>", EsoGrinderWip.version))
    EsoGrinderWip.Print(zo_strformat ( "ESO API Version =  <<1>>", EsoGrinderWip.version_eso_api))
end

SLASH_COMMANDS["/egrdebug"] = EsoGrinderWip.OnSlashCommandDebug
SLASH_COMMANDS["/egrstart"] = EsoGrinderWip.OnSlashCommandStart
SLASH_COMMANDS["/egrstop"] = EsoGrinderWip.OnSlashCommandStop
SLASH_COMMANDS["/egrversion"] = EsoGrinderWip.OnSlashCommandVersion

function EsoGrinderWip.EventCurrencyUpdateHandler(eventCode, currencyType, currencyLocation, newAmount, oldAmount, thisReason )
    EsoGrinderWip.DebugPrintInFunction("EventCurrencyUpdateHandler")

    local new_amount = newAmount
    local old_amount = oldAmount
    local delta_amount = new_amount - old_amount
    local currency_type = currencyType
    local currency_location = currencyLocation
    local reason = thisReason
    local use_ecl = true

    if use_ecl then
        d ( "Using esoui_constants_live.lua functions." )
        currency_type = CurrencyType_get_string(currencyType)
        currency_location = CurrencyLocation_get_string(currencyLocation)
        reason = CurrencyChangeReason_get_string(thisReason)
    end

    z = zo_strformat ( "eventCode=<<1>>, currencyType=<<2>>=<<3>>, currencyLocation=<<4>>=<<5>>,",
            eventCode,
            currencyType,
            currency_type,
            currencyLocation,
            currency_location)

    z2 = zo_strformat ( "<<1>> reason=<<2>>=<<3>>, newAmount=<<4>>, oldAmount=<<5>>, delta_amount=<<6>>",
            z,
            thisReason,
            reason,
            newAmount,
            oldAmount,
            delta_amount)

    EsoGrinderWip.DebugPrint(z2)
end

function EsoGrinderWip:Initialize()
    self.ddebug = true

    EsoGrinderWip.DebugPrintInFunction("Initialize")

    self.RegisterForAllEvents()
end

function EsoGrinderWip:DelayedStartedMessage()
    EsoGrinderWip.DebugPrintInFunction("DelayedStartedMessage")
end

function EsoGrinderWip.OnAddOnLoaded(event, addonName)
    EsoGrinderWip.function_call_count = 0
    EsoGrinderWip.DebugPrintInFunction("OnAddOnLoaded")

    if addonName == EsoGrinderWip.name then
        EsoGrinderWip:Initialize()
        EVENT_MANAGER:UnregisterForEvent(EsoGrinderWip.name,EVENT_ADD_ON_LOADED)
        zo_callLater(EsoGrinderWip.DelayedStartedMessage, 1000)
    end
end

EVENT_MANAGER:RegisterForEvent(EsoGrinderWip.name, EVENT_ADD_ON_LOADED, EsoGrinderWip.OnAddOnLoaded)
