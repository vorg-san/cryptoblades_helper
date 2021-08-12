import './App.css'
import React, {useState, useEffect, useCallback} from 'react'
import {apiMy} from './components/api'
import Loading from './components/Loading'
import moment from 'moment'
import {getFinalPrice, fromEther} from './web3'

function App() {
	const [weapons, setWeapons] = useState();

	const loadDB = useCallback(async () => {
		let weapons = await apiMy('weapons')
		// weapons.sort((a,b) => b.powerPerPrice - a.powerPerPrice)
		// for (let i = 0; i < weapons.length; i++) {
		// 	if(i > 20) break

		// 	let realPrice = parseFloat(fromEther(await getFinalPrice(weapons[i].weaponId)))

		// 	if(weapons[i].price !== realPrice) {
		// 		console.log(weapons[i].price, realPrice)
		// 		weapons[i].price = realPrice
		// 		weapons[i].powerPerPrice = weapons[i].power / weapons[i].price
		// 		apiMy('update_price', {weaponId: weapons[i].weaponId, price: weapons[i].price})
		// 	}
		// }
		setWeapons(weapons)
	}, [])

	useEffect(() => {
		loadDB()
	}, [loadDB]);

	async function readWeapons() {
		await apiMy('load_weapons')
		loadDB()
	}

	async function cleanWeapons() {
		await apiMy('clean_weapons')
		loadDB()
	}

	async function doFights() {
		apiMy('do_fights')
	}

	async function readWeaponsBSC() {
		await apiMy('weapons_bsc')
		loadDB()
	}

  return (
		<>
		<main className="content">
			<div className="row">
				<button type='button' className="btn btn-primary" onClick={readWeapons}>
					Load from CB market
				</button>
				<button type='button' className="btn btn-primary" onClick={readWeaponsBSC}>
					Load from BSC
				</button>
				<button type='button' className="btn btn-primary" onClick={cleanWeapons}>
					Clean Weapons
				</button>
				<button type='button' className="btn btn-primary" onClick={doFights}>
					Fight!
				</button>
			</div>

			<div className="row">
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
									<td>{w.weaponStars}* {w.weaponElement}</td>
									<td>{w.stat1Value} {w.stat1Element}</td>
									<td>{w.stat2Value} {w.stat2Element}</td>
									<td>{w.stat3Value} {w.stat3Element}</td>
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
		</main>
		<Loading />
		</>
  )
}

export default App
