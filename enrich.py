# Stijn Henckens
# June 2020
#
# Enriches a conditional preference network (CPN_1) with features and/or values
# from conditional preference network (CPN_2).
# Prints CPN_1 and CPN_2, followed by the enriched CPN_1.
# Note: CPNs need to be paths to .json files (see README.md)
#
# Usage: python3 enrich.py <path to CPN_1> <path to CPN_2>

import sys
from CPnet import CPnet


def main():
    if len(sys.argv) != 3:
        print("usage: python3 enrich.py <path to CPN_1.json> \
                      <path to CPN_2.json>")
        return 1

    CPN_1 = CPnet(sys.argv[1])
    CPN_2 = CPnet(sys.argv[2])
    CPN_enrich = CPnet(sys.argv[1])

    print(CPN_1)
    print(CPN_2)
    enrich(CPN_enrich, CPN_2)
    CPN_enrich.make_json()
    print(CPN_enrich)
    return 0


def enrich(CPN_1, CPN_2):
    # Decompose both CPnets
    CPN_1.decompose()
    CPN_2.decompose()

    # Iterate through features
    for feature in CPN_2.get_features():
        # Add unknown feature
        if not feature in CPN_1.get_features():
            CPN_1.add_feature(feature)

        new_domain = CPN_2.get_CPT(feature)["domain"]
        # Adopt domain
        CPN_1.add_domain(feature, new_domain)

        # Check every condition
        for condition in CPN_2.get_conditions(feature):
            preference = CPN_2.get_preference(feature, condition)
            regardless = CPN_2.get_regardless(feature, condition)
            if len(CPN_1.get_CPT(feature)["pref_relations"]) == 0:
                CPN_1.complete_merge(feature, condition, preference, regardless)
            elif not condition in CPN_1.get_conditions(feature):
                CPN_1.complete_merge(feature, condition, preference, regardless)
            else:
                if check_equal_preference(CPN_1, CPN_2, feature, condition):
                    continue
                if check_unequal_preference(CPN_1, CPN_2, feature, condition):
                    CPN_1.complete_merge(feature, condition, \
                                         preference, regardless)
                else:
                    CPN_1.partial_merge(feature, condition, \
                                        preference, regardless)
    # check regardless ?
    CPN_1.recompose()
    CPN_1.increase_enrichments(CPN_2)
    return CPN_1


def check_equal_preference(CPN_1, CPN_2, feature, condition):
    pref_1 = CPN_1.get_preference(feature, condition)
    pref_2 = CPN_2.get_preference(feature, condition)
    if pref_1 == pref_2:
        return True
    return False


def check_unequal_preference(CPN_1, CPN_2, feature, condition):
    pref_1 = CPN_1.get_preference(feature, condition)
    pref_2 = CPN_2.get_preference(feature, condition)
    if len(pref_1) > len(pref_2):
        if any(check in pref_2 for check in pref_1):
            return False
        return True
    else:
        if any(check in pref_1 for check in pref_2):
            return False
        return True


if __name__ == "__main__":
    main()
