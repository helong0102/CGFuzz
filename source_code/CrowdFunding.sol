pragma solidity ^0.4.26;

contract CrowdFunding {
    uint256 goal = 300 ether;
    uint256 raised = 0; /*0: Activate 1:Finished*/
    uint256 phase = 0;
    address beneficiary = msg.sender;

    constructor () public {}

    function donate () payable public {
        /*Check if the crowdfunding goal is reached*/
        if (goal > raised) {
            raised += msg.value;
        }else {
            phase = 1;
        }
    }

    function setBeneficiary (address newOwner) public {
        // Fix : require (msg.sender == beneficiary)
        require(phase == 1);
        beneficiary = newOwner;
    }


    function withdraw() public {
        /*The crowdfunding goal has been reached*/
        require(phase == 1);
        beneficiary.call.value(raised)();
        raised = 0;
    }

}
