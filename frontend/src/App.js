import "./App.css";
import React, { useState, useEffect, useCallback } from "react";
import { apiMy } from "./components/api";
import Loading from "./components/Loading";
import moment from "moment";
import { getFinalPrice, fromEther } from "./web3";

function App() {
  const [accounts, setAccounts] = useState();
  const [myAccounts, setMyAccounts] = useState();
	const [numFights, setNumFights] = useState();
	const [bnbUsd, setBnbUsd] = useState();
	const [skillUsd, setSkillUsd] = useState();
	const [oracleSkillUsd, setOracleSkillUsd] = useState();
	const [bnbWallet, setBnbWallet] = useState();
	const [skillInGame, setSkillInGame] = useState();
	const [skillStaked, setSkillStaked] = useState();
	const [skillWallet, setSkillWallet] = useState();

	function shortAddress(a) {
		return a.substring(0,6) + '...' + a.substring(a.length - 4, a.length)
	}

	function traitPower(char_element, status_element, value) {
		return value >= 0 ? value * (char_element == status_element ? 0.002675 : (status_element == 4 ? 0.002575 : 0.0025)) : 0
	}

	function characterPower(level) {
    return ((1000 + (level * 10)) * (Math.floor(level / 10) + 1))
	}

	function get_acc(my_accs, accs, address) {
		let acc = accs.find(a => a.address === address)
		if(!acc) {
			acc = JSON.parse(JSON.stringify(my_accs.find(a => a.address === address)))
			acc.weapons = []
			acc.chars = []
			accs.push(acc)
		}
		return acc
	}

	function get_level_reach(xp_table, level, xp, xp_unclaimed) {
		xp += xp_unclaimed
		for (let i = xp_table.map(x => x.level).indexOf(level); i < xp_table.length && xp > xp_table[i].xp_required; i++) {
			level++
			xp -= xp_table[i].xp_required
		}
		return level
	}

	const loadItems = useCallback(async () => {
		let my_accs = await apiMy('personal_account')
		let xp_table = await apiMy('experience_table')
		let price = await apiMy('price')
		
		let accs = []

		let chars = await apiMy("characters")
		chars.map(c => {
			let acc = get_acc(my_accs, accs, c.owner)
			c.level_reach = get_level_reach(xp_table, c.level, c.xp, c.xp_unclaimed)
			acc.chars.push(c)
		})

		let weapons = await apiMy("weapons")
		weapons.map(w => {
			let acc = get_acc(my_accs, accs, w.owner)
			w.traitsPower = [];
			[0,1,2,3].map(i => 
				w.traitsPower.push((1 + (
					traitPower(i, w.stat1Element, w.stat1Value) +
					traitPower(i, w.stat2Element, w.stat2Value) +
					traitPower(i, w.stat3Element, w.stat3Value) 
				)) * (i == w.weaponElement ? 1.075 : 1))
			)
			acc.weapons.push(w)
		})

		accs.map(acc => {
			for (let i = 0; i < Math.max(acc.chars?.length,acc.weapons?.length); i++) {
				let item = {}
				if(i === 0) {
					acc.items = []
					item.owner = acc.owner
				}
				item.char = acc.chars[i]
				item.weapon = acc.weapons[i]
				acc.items.push(item)
			}
			acc.chars = null
			acc.weapons = null
		})

		accs.sort((a, b) => parseInt(a.name.split(' ')[1]) - parseInt(b.name.split(' ')[1]))

		let bnb = 0
		let skill_in_game = 0
		let skill_staked = 0
		let skill = 0
		
		accs.map(a => {
			bnb += a.bnb
			skill_in_game += a.skill_in_game
			skill_staked += a.skill_staked
			skill += a.skill
		})

		setBnbWallet(bnb)
		setSkillInGame(skill_in_game)
		setSkillStaked(skill_staked)
		setSkillWallet(skill)

		// let rem = ['acc 1','acc 2','acc 3','acc 4','acc 5','acc 6','acc 7','acc 8',
		// 'acc 12','acc 13','acc 14','acc 9','acc 16','acc 19','acc 11','acc 10','acc 15',]
		// accs = accs.filter(a => !rem.includes(a.name))
		// my_accs = my_accs.filter(a => !rem.includes(a.name))

		setAccounts(accs)
		setMyAccounts(my_accs)
		setBnbUsd(price[0].value)
		setSkillUsd(price[1].value)
		setOracleSkillUsd(price[2].value)
	}, [])

  useEffect(() => {
    loadItems()
  }, []);

  async function syncMarket() {
    apiMy("read_market_weapons");
    apiMy("read_market_chars");
    apiMy("clean_weapons");
    apiMy("clean_chars");
    setTimeout(() => window.location.href = '/', 6000)
  }

  async function claimRewards() {
    apiMy("from_game_to_stake");
  }

  async function doFights() {
    apiMy("do_fights", {max_num_figths : numFights});
  }

  async function update_experience_table() {
    apiMy("update_experience_table");
  }	

  async function updateItemsAccount() {
    await apiMy("update_items_account");
		loadItems()
  }

  function getIconElement(e) {
		if(e === undefined) return;
    let elements = ["fire", "earth", "lightning", "water", "power"];
    let name = elements[e] + "-icon";
    return <span className={name}></span>;
  }

	async function transferChar(from, to, charId) {
		if(window.confirm('tem certeza?')) {
			let tx_hash = await apiMy('transfer_character', {from: from, to: to, charId: charId})

			if(tx_hash?.startsWith('0x')) {
				window.open('https://bscscan.com/tx/' + tx_hash)
				await apiMy('update_items_account', {accounts: [from, to]});
				loadItems()
			} else
				alert('Error: ' + tx_hash)
		}
	}

	async function transferWeapon(from, to, weaponId) {
		if(window.confirm('tem certeza?')) {
			let tx_hash = await apiMy('transfer_weapon', {from: from, to: to, weaponId: weaponId})

			if(tx_hash?.startsWith('0x')) {
				window.open('https://bscscan.com/tx/' + tx_hash)
				await apiMy('update_items_account', {accounts: [from, to]});
				loadItems()
			} else
				alert('Error: ' + tx_hash)
		}
	}

  return (
    <>
      <main className="content">
        <div className="row">
          <div className="col-11 offset-1">
            <button
              type="button"
              className="btn btn-primary"
              onClick={syncMarket}
            >
              Sync Market
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={updateItemsAccount}
            >
              Update my items
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={update_experience_table}
            >
              XP Table
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={claimRewards}
            >
              Stake Rewards
            </button>
						<input type="number" style={{width: '50px'}} onChange={(e) => setNumFights(e.target.value)} />
            <button type="button" className="btn btn-danger" onClick={doFights}>
              Fight!
            </button>
          </div>
        </div>

				<br/><br/>

				<div className="row">
          <div className="col-2">
						BNB: {bnbWallet?.toFixed(2)}<br/>
						$ {(bnbWallet * bnbUsd)?.toFixed(2)}
					</div>
          <div className="col-2">
						Skill: {skillWallet?.toFixed(2)}<br/>
						$ {(skillWallet * skillUsd)?.toFixed(2)}
					</div>
          <div className="col-2">
						Skill staked: {skillStaked?.toFixed(2)}<br/>
						$ {(skillStaked * skillUsd)?.toFixed(2)}
					</div>
          <div className="col-2">
						Skill in game: {skillInGame?.toFixed(2)}<br/>
						$ {(skillInGame * skillUsd)?.toFixed(2)}
					</div>
          <div className="col-2">
						Total: $ {((skillInGame + skillStaked + skillWallet) * skillUsd + bnbWallet * bnbUsd)?.toFixed(2)}
					</div>
				</div>        

				<br/><br/>

				<div className="row">
          <div className="col-11 offset-1">
            {accounts && (
              <table className="table">
                <thead>
                  <tr>
                    <td rowSpan='2'></td>
                    <td rowSpan='2'>Address</td>
                    <td colSpan='3'>Chars</td>
                    <td colSpan='5'>Weapons</td>
									</tr>
									<tr>
										<td>ID</td>
										<td>Power</td>
										<td>Level</td>
										<td>ID</td>
										<td>Stats</td>
										<td>{getIconElement(0)}</td>
										<td>{getIconElement(1)}</td>
										<td>{getIconElement(2)}</td>
										<td>{getIconElement(3)}</td>
                  </tr>
                </thead>
                <tbody>
									{accounts.map((acc, accIndex) => (
										<>
										{acc.items.map((item, index) => (
                    	<tr key={index}>
												{index === 0 && (
													<>
													<td rowSpan={accounts[accIndex].items.length}>{acc.name}</td>
													<td rowSpan={accounts[accIndex].items.length}>
														{shortAddress(acc.address)}<br/>
														{acc.bnb.toFixed(3)} bnb ${(acc.bnb * bnbUsd).toFixed(0)}<br/>
														{acc.skill.toFixed(3)} skill<br/>
														{acc.skill_staked.toFixed(3)} staked<br/>
														{acc.skill_in_game.toFixed(3)} in game
														
													</td>
													</>
												)}
												<td>
													{item?.char?.charId} {getIconElement(item?.char?.element)}
													{item?.char && (
														<select onChange={e => transferChar(acc.address, e.target.value, item?.char?.charId)}>
															<option value={''}></option>
															{myAccounts?.map((acc, index) => (
																<option value={acc.address} key={index}>{acc.name}</option>
															))}
														</select>
													)}
												</td>
												<td>{item?.char?.power}</td>
												<td>
													{item?.char && (
														<span className={parseInt(item.char.level_reach / 10) - parseInt(item.char.level / 10) >= 1 ? 'green' : ''}>
															{item.char.level} ({item.char.level_reach})
														</span>
													)}
												</td>
												<td>
													{item?.weapon?.weaponId} {getIconElement(item?.weapon?.weaponElement)}
													{item?.weapon && (
														<select onChange={e => transferWeapon(acc.address, e.target.value, item?.weapon?.weaponId)}>
															<option value={''}></option>
															{myAccounts?.map((acc, index) => (
																<option value={acc.address} key={index}>{acc.name}</option>
															))}
														</select>
													)}
												</td>
												<td>													
													{item?.weapon?.stat1Value} {getIconElement(item?.weapon?.stat1Element)}
													{!!item?.weapon?.stat2Value && (
														<>
															{item?.weapon?.stat2Value} {getIconElement(item?.weapon?.stat2Element)}
														</>
													)}
													{!!item?.weapon?.stat3Value && (
														<>
															{item?.weapon?.stat3Value} {getIconElement(item?.weapon?.stat3Element)}
														</>
													)}
												</td>
												{item?.weapon?.traitsPower?.map((v, index) => (
													<td key={index}>{v.toFixed(2)}{getIconElement(index)}</td>
												))}
											</tr>
										))}
										</>
									))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
      <Loading />
    </>
  );
}

export default App;
