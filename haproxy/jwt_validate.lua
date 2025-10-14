-- JWT validation script for HAProxy
-- This script validates JWT tokens and checks for admin role

local base64 = require("base64")
local json = require("json")

-- Function to decode base64 URL-safe
local function base64url_decode(str)
    -- Replace URL-safe characters
    str = str:gsub("-", "+"):gsub("_", "/")
    -- Add padding if needed
    local padding = 4 - (str:len() % 4)
    if padding ~= 4 then
        str = str .. string.rep("=", padding)
    end
    return base64.decode(str)
end

-- Function to validate JWT and check admin role
function validate_admin_jwt(txn)
    local auth_header = txn.sf:req_fhdr("authorization")
    
    if not auth_header or not auth_header:match("^Bearer ") then
        return false
    end
    
    local token = auth_header:match("Bearer (.+)")
    if not token then
        return false
    end
    
    -- Split JWT token into parts
    local parts = {}
    for part in token:gmatch("[^%.]+") do
        table.insert(parts, part)
    end
    
    if #parts ~= 3 then
        return false
    end
    
    -- Decode the payload (second part)
    local payload_encoded = parts[2]
    local payload_json = base64url_decode(payload_encoded)
    
    if not payload_json then
        return false
    end
    
    -- Parse JSON payload
    local payload = json.decode(payload_json)
    if not payload then
        return false
    end
    
    -- Check for admin role
    local realm_access = payload.realm_access
    if realm_access and realm_access.roles then
        for _, role in ipairs(realm_access.roles) do
            if role == "admin" then
                return true
            end
        end
    end
    
    return false
end

-- Register the function
core.register_fetches("validate_admin_jwt", validate_admin_jwt)
