

def count_total_f2p_p2f_of_file(mbfl_results):

    for filename in mbfl_results:
        total_f2p = 0
        total_p2f = 0
        for line in mbfl_results[filename]["lines"]:
            f2p = mbfl_results[filename]["lines"][line]['total_features']['total_f2p']
            p2f = mbfl_results[filename]["lines"][line]['total_features']['total_p2f']
            total_f2p += f2p
            total_p2f += p2f

        mbfl_results[filename]['total_f2p'] = total_f2p
        mbfl_results[filename]['total_p2f'] = total_p2f
    
    return mbfl_results


def calc_susp_score(mbfl_results):

    # this calculates total f2p and p2f of a FILE
    mbfl_results = count_total_f2p_p2f_of_file(mbfl_results)

    for filename in mbfl_results:
        file_f2p = mbfl_results[filename]['total_f2p']
        file_p2f = mbfl_results[filename]['total_p2f']
        
        for line in mbfl_results[filename]["lines"]:
            # this calculates total mutants of a LINE
            num_mutants = mbfl_results[filename]["lines"][line]['total_features']['mutant_cnt']
            
            muse_1 = (1 / ((num_mutants + 1) * (file_f2p + 1)))
            muse_2 = mbfl_results[filename]["lines"][line]['total_features']['total_f2p']
            muse_3 = (1 / ((num_mutants + 1) * (file_p2f + 1)))
            muse_4 = mbfl_results[filename]["lines"][line]['total_features']['total_p2f']

            final_muse = (muse_1*muse_2) - (muse_3*muse_4)
            mbfl_results[filename]["lines"][line]['suspiciousness'] = final_muse

    import json
    print(json.dumps(mbfl_results, indent=4))
    
    return mbfl_results


def show_in_order(mbfl_results):
    lines = "lines"
    # show mbfl line information in order of suspiciousness
    for filename in mbfl_results:
        for line in mbfl_results[filename]["lines"]:
            print(f"{filename}:{line} - {mbfl_results[filename][lines][line]['suspiciousness']}")
