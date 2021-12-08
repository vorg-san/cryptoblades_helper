const {NFTMarket} = require('./contracts')

const Web3 = require('web3');


const stakingRewardAddress = '0xd6b2D8f59Bf30cfE7009fB4fC00a7b13Ca836A2c';
const conStakingTokenAddress = '0x154a9f9cbd3449ad22fdae23044319d6ef2a1fab';
const mainAddress = '0x39Bea96e13453Ed52A734B6ACEeD4c41F57B2271';
const charAddress = '0xc6f252c2cdd4087e30608a35c022ce490b58179b';
const weapAddress = '0x7e091b0a220356b157131c831258a9c98ac8031a';
const oracleAddress = '0x1cbfa0ec28da66896946474b2a93856eb725fbba';
const marketAddress = '0x90099dA42806b21128A094C713347C7885aF79e2';
const defaultAddress = '0x0000000000000000000000000000000000000000';

const web3 = new Web3('https://bsc-dataseed1.defibit.io/');

// const conStakingReward = new web3.eth.Contract(IStakingRewards, stakingRewardAddress);
// const conStakingToken = new web3.eth.Contract(IERC20, conStakingTokenAddress);
// const conCryptoBlades = new web3.eth.Contract(CryptoBlades, mainAddress);
// const conCharacters = new web3.eth.Contract(Characters, charAddress);
// const conWeapons = new web3.eth.Contract(Weapons, weapAddress);
const conMarket = new web3.eth.Contract(NFTMarket, marketAddress);
// const conOracle = new web3.eth.Contract(BasicPriceOracle, oracleAddress);

// const isAddress = address => web3.utils.isAddress(address);
// const getBNBBalance = address => web3.eth.getBalance(address);
// const fromEther = (value) => web3.utils.fromWei(BigInt(value).toString(), 'ether');

// export const getRewardsPoolBalance = () => conStakingToken.methods.balanceOf(mainAddress).call({ from: defaultAddress });
// export const getStakingPoolBalance = () => conStakingToken.methods.balanceOf(stakingRewardAddress).call({ from: defaultAddress });

// const getStakedBalance = address => conStakingToken.methods.balanceOf(address).call({ from: defaultAddress });
export const fromEther = (value) => web3.utils.fromWei(BigInt(value).toString(), 'ether');
export const getFinalPrice = async (tokenId, contract) => conMarket.methods.getFinalPrice(contract || weapAddress, tokenId).call({ from: defaultAddress })