def find(tokens: list[str], entity: list[str]) -> int:
    # Python program for KMP Algorithm
    # https://www.geeksforgeeks.org/python-program-for-kmp-algorithm-for-pattern-searching-2/
    def KMPSearch(pat, txt) -> list[int]:
        M = len(pat)
        N = len(txt)

        result = []

        # create lps[] that will hold the longest prefix suffix
        # values for pattern
        lps = [0] * M
        j = 0  # index for pat[]

        # Preprocess the pattern (calculate lps[] array)
        computeLPSArray(pat, M, lps)

        i = 0  # index for txt[]
        while i < N:
            if pat[j] == txt[i]:
                i += 1
                j += 1

            if j == M:
                result.append(i - j)
                # print("Found pattern at index " + str(i-j))
                j = lps[j - 1]

            # mismatch after j matches
            elif i < N and pat[j] != txt[i]:
                # Do not match lps[0..lps[j-1]] characters,
                # they will match anyway
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        return result

    def computeLPSArray(pat, M: int, lps: list[int]):
        len = 0  # length of the previous longest prefix suffix

        assert lps[0] == 0
        i = 1

        # the loop calculates lps[i] for i = 1 to M-1
        while i < M:
            if pat[i] == pat[len]:
                len += 1
                lps[i] = len
                i += 1
            else:
                # This is tricky. Consider the example.
                # AAACAAAA and i = 7. The idea is similar
                # to search step.
                if len != 0:
                    len = lps[len - 1]

                    # Also, note that we do not increment i here
                else:
                    lps[i] = 0
                    i += 1

    cand_id = KMPSearch(entity, tokens)
    assert len(cand_id) > 0
    id = cand_id[0]

    return id
