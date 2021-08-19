import './App.css'
import React, {useState, useEffect, useCallback} from 'react'
import {apiMy} from './components/api'
import Loading from './components/Loading'
import moment from 'moment'
import {getFinalPrice, fromEther} from './web3'

function App() {
	const [weapons, setWeapons] = useState();

	const loadDB = useCallback(async () => {
		let weapons = [] //await apiMy('weapons')
		setWeapons(weapons)
	}, [])

	useEffect(() => {
		loadDB()
	}, [loadDB]);

	async function syncMarket() {
		apiMy('read_market_weapons')
		apiMy('read_market_chars')
		apiMy('clean_weapons')
		apiMy('clean_chars')
		// window.location = '/'
	}

	async function claimRewards() {
		apiMy('from_game_to_stake')
	}

	async function doFights() {
		apiMy('do_fights')
	}

	function getIconElement(e) {
		let elements = ['fire', 'earth', 'lightning', 'water']
		let name = elements[e] + '-icon'
		return (
			<span className={name}></span>
			)
	}

  return (
		<>
		<main className="content">
			<div className="row">
			<div className="col-11 offset-1">
				<button type='button' className="btn btn-primary" onClick={syncMarket}>
					Sync Market
				</button>
				<button type='button' className="btn btn-primary" onClick={claimRewards}>
					Stake Rewards
				</button>
				<button type='button' className="btn btn-danger" onClick={doFights}>
					Fight!
				</button>
			</div>
			</div>

			<div className="row">
			<div className="col-11 offset-1">
				{weapons && (
					<table className='table'>
						<thead>
							<tr>
								<td>ID</td>
								<td>Weapon</td>
								<td>Stat 1</td>
								<td>Stat 2</td>
								<td>Stat 3</td>
								<td>Power</td>
								<td>Price</td>
								<td>Power/Price</td>
								<td></td>
							</tr>
						</thead>
						<tbody>
							{weapons?.map((w, index) => (
								<tr key={index}>
									<td>{w.weaponId}</td>
									<td>{w.weaponStars+1}* {getIconElement(w.weaponElement)}</td>
									<td>{w.stat1Value} {getIconElement(w.stat1Element)}</td>
									<td>{!!w.stat2Value && (
										<>{w.stat2Value} {getIconElement(w.stat2Element)}</>
									)}</td>
									<td>{!!w.stat3Value && (
										<>{w.stat3Value} {getIconElement(w.stat3Element)}</>
									)}</td>
									<td>{w.power.toFixed(2)}</td>
									<td>{w.price.toFixed(2)}</td>
									<td>{w.powerPerPrice.toFixed(2)}</td>
									<td>{w.sellerAddress} {w.weaponId} {w.price * 1000000000000000000}</td>
								</tr>
							))}			
						</tbody>
					</table>
				)}
			</div>
			</div>
		</main>
		<Loading />
		</>
  )
}

export default App
