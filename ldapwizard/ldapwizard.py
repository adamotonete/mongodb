import sys



def showConfig(_cfg):
    print('------------------------------------------------------------------------------')
    print("")
    print('security:')
    print('    authorization: "enabled"')
    print('ldap:')
    if _cfg["usessl"] == "n":
        print('    transportSecurity : "none"')
    print('    servers: ' + _cfg["ldap_server"])
    if _cfg["use_userToDNMapping"] == "y":
        print('    userToDNMapping: ' + _cfg["userToDNMapping"])
    if _cfg["ldap_authorization"] == "y":
        print('    bind:')
        print('        queryUser: ' + _cfg["bind_user"])
        print('        queryPassword: "<yourpassword>"')
        print('    authz:')
        print('        queryTemplate: ' + _cfg["queryTemplate"])
    print('setParameter:')
    print('    authenticationMechanisms: PLAIN' + _cfg["authenticationMechanisms"])
    print("")
    print('------------------------------------------------------------------------------')
    print("")

def valid_exit(current_value):
    if current_value == "0":
        sys.exit(0)

def textbox(default_value, _example = ""):
    resp = ""
    if _example != "" and default_value != "":
        resp = input(_example + " " + "default [%s] > " % (default_value))
    if _example == "" and default_value != "":
        resp = input("default [%s] > " % (default_value))
    if _example == "" and default_value == "":
        resp = input(" > ")
    if _example != "" and default_value == "":
        resp = input(_example + "  > ")

    if resp == "": resp = default_value;
    valid_exit(resp)
    while resp == "":
        resp = textbox(default_value,_example)
    return resp;


def yesnobox(default_value):
    resp = input("(y)es/(n)o - default [%s] > " % (default_value))
    if resp == "" : resp = default_value;
    valid_exit(resp)
    while resp not in ["0", "y", "n"]:
        resp  = yesnobox(default_value)
    return resp;

def numeredList(list, default_value):
    x = 1;
    for i in list:
        print("  " + str(x) + ". " + str(i))
        x=x+1;
    resp = input(" default [%s] > " % (default_value))
    if resp == "" : resp = default_value;
    valid_exit(resp)
    while int(resp) > len(list) or int(resp) < 0:
        resp = numeredList(list, default_value)
    return resp;

def dcDomain(_domain):
    result = ""
    for d in _domain.split("."):
        if result != "": result = result + ','
        result = result + 'DC=' + d
    return result

def questions():

    config = {}
    domain = ""
    group_search_limit = "n"
    users_group_search = ""
    group_search = ""
    usessl = ""
    users_group = ""

    # Header
    print("Welcome to LDAP wizard")
    print("Type 0 anytime to leave the program")
    print("-------------------------------------")
    print("Before you begin please make sure that:")
    print("1. You are using MongoDB Enterprise Version")
    print("2. Your LDAP server is reacheable by your mongod, \n"
          "   the default LDAP ports are 636 (ldap) and 389 (ldaps - ssl)")
    print("3. You are using MongoDB Enterprise Version")
    print("-------------------------------------")

    # LDAP Server
    print("What is your LDAP server fully qualified name or servers IP?")
    ldap_server= textbox("","ex. myldap.mydomain.com")
    valid_exit(ldap_server)
    config["ldap_server"] = ldap_server

    # Domain name
    print("What is your domain name?")
    if not ldap_server.replace(".", "").isdecimal():
        for dc in ldap_server.split('.')[1::]:
            if domain != "":
                domain += '.'
            domain += dc

    domain = textbox(domain,"")
    config["domain"] = domain;

    # Using use_userToDNMapping
    print("Do you plan to use anything different than the User Distinguished Name to login to the database?")
    use_userToDNMapping = yesnobox("y")
    config["use_userToDNMapping"] = use_userToDNMapping

    # Confirming Active Directory of OpenLDAP (this will change the configuration)
    print("Are you configuring an:")
    opt = ['Active Directory', 'OpenLDAP']
    ad_ldap = numeredList(opt, 1)
    valid_exit(ad_ldap)
    # 1 - Active Directory, 2 OpenLDAP
    config["ldap_program"] = opt[int(ad_ldap) - 1]

    if use_userToDNMapping == "y":
        print("What LDAP attribute would you like to use to perform the authentication?")
        if int(ad_ldap) == 1:
            opt = ['UserPrincipalName (person@domain.com)', 'sAMAccountName (person)']
        if int(ad_ldap) == 2:
            opt = ['uid - person']

        login_attribute = numeredList(opt, 1)
        login_method = opt[int(login_attribute) - 1].split(" ")[0].strip()

        config["login_method"] = login_method
        valid_exit(login_attribute)
        # 1 - Active Directory, 2 Open LDAP, 3 Other.

    # asking about SSL
    print("Is this ldap server configured with SSL? (ldaps?)")
    usessl = yesnobox("y")
    config["usessl"] = usessl

    # Bind DN for users.
    print("Are the users in a specific group that you want to limit the search by?")
    users_group = yesnobox("n")

    config["users_group"] = users_group

    if users_group == 'y':
        print("What is the distinguised name where mongod need to search users?")
        users_group_search= textbox("CN=Users," + dcDomain(domain),"")
        valid_exit(users_group)
        config["users_group_search"] = users_group_search


    # Bind DN for users - Setting the user.

    print("Would you like to configure LDAP authorization as well?. LDAP authorization will allow group authorization")
    print("more info: https://docs.mongodb.com/manual/core/security-ldap-external/")
    ldap_authorization = yesnobox("y")
    config["ldap_authorization"] = ldap_authorization

    if ldap_authorization == "y":
        print("Would you like to change the search base to only look on a specific part of the tree?")
        group_search_limit = yesnobox("n")
        config["group_search_limit"] = group_search_limit

        if group_search_limit == "y":
            group_search = textbox("OU=Groups," + dcDomain(domain),"")
            config["group_search"] = group_search

        print("LDAP authorization requires a dedicated user to find what groups an LDAP user belongs to\n"
              "please specify the user that mongodb will use to bind the communicate to LDAP server")

        if int(ad_ldap) == 1:
            print('Microsoft Active directory allows either the Distinguished Name or the UserPrincipalName')
            bind_user = textbox("", "user@" + domain)
            config["bind_user"] = bind_user
        else:
            print("Please specify the DistinguishedName of the user that will be used")
            bind_user = textbox("", "e.g: DN=bind_user,OU=System Users," + dcDomain(domain))
            config["bind_user"] = bind_user

    if int(ad_ldap) == 1:
        if ldap_authorization == "y":
            if group_search == "":
                config["queryTemplate"] = "\"{USER}?memberOf?base\""
            else:
                config["queryTemplate"] = "\""+ group_search + "??sub?(&(objectClass=group)" \
                                                               "(member:1.2.840.113556.1.4.1941:={USER}))\""
        if use_userToDNMapping == "y":
            if  users_group_search == "":
                config["userToDNMapping"] = '[{match: "(.+)", ldapQuery: "' + dcDomain(domain) + \
                                        '?dn?sub?(&(objectClass=user)(' + login_method + '={0}))"}]'
            else:
                config["userToDNMapping"] = '[{match: "(.+)", ldapQuery: "' + users_group_search + \
                                            '?dn?sub?(&(objectClass=user)(' + login_method + '={0}))"}]'
    elif int(ad_ldap) == 2:
        if ldap_authorization == "y":
            if group_search == "":
                config["queryTemplate"] = "\"" + dcDomain(domain) + "??sub?(memberUid={PROVIDED_USER})\""
            else:
                config["queryTemplate"] = "\"" + group_search + "??sub?(memberUid={PROVIDED_USER})\""
            if use_userToDNMapping == "y":
                if users_group_search == "":
                    config["userToDNMapping"] = '[{match: "(.+)", ldapQuery: "' + dcDomain(domain) + \
                                            '?dn?sub?(&(objectClass=posixAccount)('+ login_method +'={0}))"}]'
                else:
                    config["userToDNMapping"] = '[{match: "(.+)", ldapQuery: "' + users_group_search + \
                                                '?dn?sub?(&(objectClass=posixAccount)(' + login_method + '={0}))"}]'


    print("Additionally to LDAP authentication, would you like to use another authenticationMechanisms?")
    authenticationMechanisms = textbox("SCRAM-SHA-256,SCRAM-SHA-1,MONGODB-X509","SCRAM-SHA-256,SCRAM-SHA-1")
    if authenticationMechanisms != "":
        config["authenticationMechanisms"] = "," + authenticationMechanisms

    showConfig(config)

    print("Would you like to dump the variables set for analysis?")
    if yesnobox("n") == "y": print(config)

# Press the green button in the gutter to run the script.

if __name__ == '__main__':
     questions()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
