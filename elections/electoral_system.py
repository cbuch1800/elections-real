import random
import time
from pprint import pprint

CANDIDATES = ("A","B","C","D","E","F","G","H","I","J","K")

def GetVotes(VoterCount):
    #Generates a set of randomised ballot papers
    AllBallots = []
    for i in range(VoterCount):
        # Change the below arg to 0 to also generate empty ballots
        BallotLen = random.randint(1,len(CANDIDATES))
        BallotOrder = random.sample(CANDIDATES, BallotLen)
        AllBallots.append(BallotOrder)
    return AllBallots

def CountFirstChoice(Ballots):
    #Count the number of votes each candidate has and returns info in dictionary
    Result = {}
    for i in RemainingCandidates:
        CandidateVotes = 0
        for Vote in Ballots:
            if Vote == []:
                pass
            elif Vote[0] == i:
                CandidateVotes += 1
        Result[i] = CandidateVotes
    # pprint(Result)
    return Result

def EliminateCandidate(Result, RoundOne):
    #Determines the candidate with the lowest vote and removes them from RemainingCandidates
    Eliminated = []
    for key, val in Result.items():
        if len(Eliminated) == 0 or val < Result.get(Eliminated[0]):
            Eliminated = [key]
        elif val == Result.get(Eliminated[0]):
            Eliminated.append(key)

    # Determines what to do if 2 candidates have the same vote
    if len(Eliminated) > 1:
        LowestCandidate = [Eliminated[0]]
        for i in Eliminated:
            if RoundOne[i] < RoundOne[LowestCandidate[0]]:
                LowestCandidate = [i]
            elif RoundOne[i] == RoundOne[LowestCandidate[0]]:
                LowestCandidate.append(i)
        Eliminated = [random.choice(LowestCandidate)]

    for Candidate in RemainingCandidates:
        if Candidate in Eliminated:
            RemainingCandidates.remove(Candidate)
    return RedistributeEliminated(Eliminated)


def RedistributeEliminated(Eliminated):
    #Removes all votes for eliminated candidates
    for i in Eliminated:
        for Ballot in Ballots:
            for j in range(len(Ballot)):
                if Ballot[j] == i:
                    Ballot.pop(j)
                    break
            
    RemoveBlankBallots(Ballots)       

def RoundDownQuota(f):
    #Ensures the quota rounds down
    i = int(f)
    if float(i) > f:
        i -= 1
    return i


def Droop(Ballots, Seats):
    #Calculates the quota
    return RoundDownQuota((len(Ballots)/(Seats + 1)) + 1)


def CheckQuota(Result):
    #Adds candidates that have met the quota to ElectedCandidates
    for key, val in Result.items():
        if val >= QUOTA and not key in ElectedCandidates:
            ElectedCandidates.append(key)
            for Ballot in Ballots:
                if key in Ballot[1:]:
                    Ballot.remove(key)
    

    if len(ElectedCandidates) == Seats:
        print("ELECTION OVER")
    print("Elected are: ")
    for Cand in ElectedCandidates:
        print(Cand, end=", ")
    print("\n--------")

def NumberMeetingQuota(Result):
    QuantityElected = 0
    for key, val in Result.items():
        if val >= QUOTA:
            QuantityElected += 1
    return QuantityElected

def TransferSurplusVotes(Result, Ballots):
    #Redistribute excess votes
    #Return True if a candidate now makes the quota that didnt before
    for key, val in Result.items():
        if val > QUOTA:
            RedistributeCount = val - QUOTA
            Redistribute = []

            for i in range(RedistributeCount):
                # Randomly selects which ballots will be redistributed
                if len(Redistribute) == 0:
                    Redistribute.append(random.randint(1,val))
                else:
                    while True:
                        RandomInteger = random.randint(1,val)
                        if not RandomInteger in Redistribute:
                            Redistribute.append(RandomInteger)
                            break

            # Redistributes the votes
            BallotLoopCounter = 0
            for Ballot in Ballots:
                # print(Ballot)
                if Ballot[0] == key:
                    BallotLoopCounter += 1
                    if BallotLoopCounter in Redistribute:
                        Ballot.pop(0)
            RemoveBlankBallots(Ballots)

    CheckResult = CountFirstChoice(Ballots)
    if NumberMeetingQuota(CheckResult) == NumberMeetingQuota(Result):
        return False
    else:
        return True

def RemoveBlankBallots(Ballots):
    for i in range(0,len(Ballots)):
        try:
            if len(Ballots[i]) == 0:
                Ballots.pop(i)
        except:
            break



def CountSTV(CandidatesList, BallotPapers, NumberElected):
    # Sets up the election
    global RemainingCandidates
    RemainingCandidates = list(CandidatesList)
    # print(RemainingCandidates) # A list of candidate IDs

    # Ballots = GetVotes(300)
    global Ballots
    Ballots = BallotPapers
    # pprint(Ballots) # A list of lists containing the votes

    global Seats
    Seats = NumberElected
    # print(Seats) # Integer showing how many candidates will be elected

    if len(RemainingCandidates) <= Seats:
        return RemainingCandidates

    global ElectedCandidates
    ElectedCandidates = []

    global ResultsByRound
    ResultsByRound = []

    RemoveBlankBallots(Ballots)

    global QUOTA
    QUOTA = Droop(Ballots, Seats)
    print("Quota: {}".format(QUOTA))

    while True:
        ResultsByRound.append(CountFirstChoice(Ballots))
        pprint(ResultsByRound[-1])
        CheckQuota(ResultsByRound[-1])
        RemoveBlankBallots(Ballots)
        if len(ElectedCandidates) == Seats:
            break
        elif len(ElectedCandidates) == 0:
            EliminateCandidate(ResultsByRound[-1], ResultsByRound[0])
        else:
            RemoveBlankBallots(Ballots)
            ChangeMade = TransferSurplusVotes(ResultsByRound[-1], Ballots)
            if not ChangeMade:
                EliminateCandidate(ResultsByRound[-1], ResultsByRound[0])
        # time.sleep(0.1)

    return ElectedCandidates


# ElectionResult = CountSTV(list(CANDIDATES), GetVotes(300), 6)
# print(ElectionResult)