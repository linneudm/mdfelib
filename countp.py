import re as re_

def gds_validate_simple_patterns(self, patterns, target):
    # pat is a list of lists of strings/patterns.  We should:
    # - AND the outer elements
    # - OR the inner elements
    found1 = True
    for patterns1 in patterns:
        found2 = False
        for patterns2 in patterns1:
            if re_.search(patterns2, target) is not None:
                found2 = True
                break
        if not found2:
            found1 = False
            break
    return found1

def validate_TDateTimeUTC(self, value):
    # Validate type TDateTimeUTC, a restriction on xs:string.
    if value is not None and Validate_simpletypes_:
        if not self.gds_validate_simple_patterns(
                self.validate_TDateTimeUTC_patterns_, value):
            warnings_.warn('Value "%s" does not match xsd pattern restrictions: %s' % (value.encode('utf-8'), self.validate_TDateTimeUTC_patterns_, ))
validate_TDateTimeUTC_patterns_ = [['^(((20(([02468][048])$|^([13579][26]))-02-29))$|^(20[0-9][0-9])-((((0[1-9])$|^(1[0-2]))-((0[1-9])$|^(1\\d)$|^(2[0-8])))$|^((((0[13578])$|^(1[02]))-31)$|^(((0[1,3-9])$|^(1[0-2]))-(29$|^30)))))T(20$|^21$|^22$|^23$|^[0-1]\\d):[0-5]\\d:[0-5]\\d([\\-,\\+](0[0-9]$|^10$|^11):00$|^([\\+](12):00))$']]

exp = [['^(((20(([02468][048])$|^([13579][26]))-02-29))$|^(20[0-9][0-9])-((((0[1-9])$|^(1[0-2]))-((0[1-9])$|^(1\\d)$|^(2[0-8])))$|^((((0[13578])$|^(1[02]))-31)$|^(((0[1,3-9])$|^(1[0-2]))-(29$|^30)))))T(20$|^21$|^22$|^23$|^[0-1]\\d):[0-5]\\d:[0-5]\\d([\\-,\\+](0[0-9]$|^10$|^11):00$|^([\\+](12):00))$']]
value = '2019-03-26T13:58:06 03:00'
found1 = True
for a in exp:
    found2 = False
    print("1 >>>", a)
    for b in a:
        print("2 >>>", b)
        if re_.search(b, value) is not None:
            found2 = True
            break
    if not found2:
        found1 = False
        break
print("3 >>> ", found1)
