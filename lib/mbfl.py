

def count_total_f2p_p2f_of_file(mbfl_results):

    for filename in mbfl_results:
        total_f2p = 0
        total_p2f = 0
        for line in mbfl_results[filename]:
            f2p = mbfl_results[filename][line]['total_features']['total_f2p']
            p2f = mbfl_results[filename][line]['total_features']['total_p2f']
            total_f2p += f2p
            total_p2f += p2f

        mbfl_results[filename]['total_f2p'] = total_f2p
        mbfl_results[filename]['total_p2f'] = total_p2f
    
    return mbfl_results


def calc_susp_score(mbfl_results):

    mbfl_results = count_total_f2p_p2f_of_file(mbfl_results)

    for filename in mbfl_results:
        file_f2p = mbfl_results[filename]['total_f2p']
        file_p2f = mbfl_results[filename]['total_p2f']
        
        for line in mbfl_results[filename]:
            num_mutants = 0

            if line == 'total_f2p' or line == 'total_p2f':
                continue

            for mutant in mbfl_results[filename][line]['mutants']:
                num_mutants += 1
            
            muse_1 = (1 / ((num_mutants + 1) * (file_f2p + 1)))
            muse_2 = mbfl_results[filename][line]['total_features']['total_f2p']
            muse_3 = (1 / ((num_mutants + 1) * (file_p2f + 1)))
            muse_4 = mbfl_results[filename][line]['total_features']['total_p2f']

            final_muse = (muse_1*muse_2) - (muse_3*muse_4)
            mbfl_results[filename][line]['suspiciousness'] = final_muse

    import json
    print(json.dumps(mbfl_results, indent=4))
    
    return mbfl_results
