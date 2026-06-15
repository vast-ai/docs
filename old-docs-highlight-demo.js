// Local CON-1518 demo helper. Do not include in the production docs PR.
// Generated from origin/main host docs to highlight content reused from the old docs.
(function () {
  const OLD_CONTENT_DEMO_ENABLED = true;
  const LOCAL_PREVIEW_HOSTS = new Set(['localhost', '127.0.0.1', '0.0.0.0', '::1']);
  const isLocalPreview = LOCAL_PREVIEW_HOSTS.has(location.hostname) || location.hostname.endsWith('.localhost');

  if (!OLD_CONTENT_DEMO_ENABLED || !isLocalPreview) return;
  if (window.__vastOldDocsHighlightDemo) return;
  window.__vastOldDocsHighlightDemo = true;

  const OLD_DOC_PHRASES = [
  {
    "t": "the min gpu setting controls the smallest gpu partition you offer. for an 8-gpu machine this determines whether customers can rent 1 2 4 or 8 gpus at a time. it s a critical lever for balancing demand capture against utilization efficiency.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "machines with datacenter gpus such as b200 h200 h100 a100 etc. and those with premium gpus such as rtx pro 6000 ws 8xrtx 5090 8xrtx 4090 etc. receive prioritized verification processing due to their high demand and performance capabilities.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "due to greater user control over hardware vm support requires iommu settings for securing pcie communications that can degrade the performance of nccl on non-rtx 40x0 multi-gpu machines that rely on pci-based gpu peer-to-peer communication.",
    "s": "vms.mdx"
  },
  {
    "t": "note that default configuration settings for most machines will not support vms and we can detect that so most hosts who do not want vms enabled do not need to take any action. configuring your machine to support vms. hardware prerequisites",
    "s": "vms.mdx"
  },
  {
    "t": "if you have confirmed your payout account is in good standing and still have not received your funds after a reasonable processing period please contact support for further review. i see my invoice is marked as pending. what does this mean",
    "s": "payment.mdx"
  },
  {
    "t": "note: meeting the minimum requirements makes your machine eligible for verification but it does not guarantee that verification will occur immediately. the final verification outcome still depends on the factors listed below. 1 reliability",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "if you operate out of a data center consider highlighting any certifications you hold e.g. tier 4 data center hipaa compliance as differentiators. these can be meaningful selling points for enterprise and compliance-sensitive customers.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "test your machines before listing and after any configuration changes. a machine that appears available but fails when rented wastes a customer s time and yours so you lose the rental and risk a negative reliability signal. verification",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "who this is for: hosts who have already completed the technical setup process and have machines ready to list. this guide covers the economic decisions that is the settings and strategies that affect your ranking occupancy and revenue.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the optimal mix depends on current market conditions so be sure to consider what your competitors are offering and where unmet demand exists. review your utilization patterns and adjust periodically. keeping your machines competitive",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this is one of the most commonly misconfigured settings. the min bid price is a floor for the bidding system not an on-demand price. customers bid above this floor and competition among bidders will drive the actual price higher.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the core tradeoff: higher prices increase revenue per rental hour but reduce occupancy. lower prices fill your machines faster but each hour earns less. the optimum sits somewhere in the middle and shifts with supply and demand.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "note: meeting the minimum requirements makes your machine eligible for verification but it does not guarantee that verification will occur immediately. the final verification outcome still depends on the factors listed below.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "we do not recommend multi-gpu hosts with datacenter gpus enable vms until we can ensure better gpu p2p communication support in vms including support for nvlink. configuring vms on your machine checking vm enablement status.",
    "s": "vms.mdx"
  },
  {
    "t": "test your machines before listing and after any configuration changes. a machine that appears available but fails when rented wastes a customer s time and yours so you lose the rental and risk a negative reliability signal.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "what it means: newly added machines or machines under evaluation. the system hasn t yet completed enough testing to confirm platform standards. this is not a judgment of quality-only that no platform guarantee exists yet.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vast.ai does not provide tax documents or tax advice to hosts residing outside the united states. international hosts are responsible for understanding and complying with their local tax obligations. united states hosts",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "pricing is the most direct lever for your earnings but the optimal price isn t simply as high as possible. rather it s the rate that maximizes total revenue given your hardware competition and current market conditions.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "do maintain consistent uptime with minimal downtime. keep network connectivity stable avoid jitter and drops. manage thermals and power to prevent throttling. proactively monitor hardware health and perform maintenance.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "when will deverification happen when the hosting software detects an error your machine is automatically but temporarily deverified. it will appear as unverified in search results until the underlying issue is resolved.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "verification is fully automated and powered by proprietary algorithms that continuously evaluate each machine s operational health and performance dynamically adjusting assessments based on real-time supply and demand.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "the offer end date is your commitment to how long you will keep the machine online and fully functional. the pricing you set is the rate you ll be paid for that commitment. together these form the terms of your offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "before your machine can be verified on vast.ai it must meet all minimum quality and reliability benchmarks. verification confirms that your machine is stable performant and properly configured to run client workloads.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "it is your responsibility to: ensure your tax information is up to date with your payment provider confirm whether you qualify for a tax form based on your earnings and location file your taxes accurately and on time",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "here s what each section means: current balance: this is the amount you ve earned so far from your referred users but haven t been paid out yet. x49 t keeps growing as your referrals continue to use the platform.",
    "s": "earning.mdx"
  },
  {
    "t": "if 200 gb of the volume offer are rented the gpu offers will reduce to 2 1xgpu 400gb offers and 1 2xgpu 800gb offer. the volume offer will still remain as there is still available space and update to offer 300gb.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "to rent your own machine you will need to first search the offers with your machine id to find the id and then create an instance using that id. the show machine command will show all your connected machines.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "from the payout history section you can: view historical payouts filter records by date range download payout records in csv format download payout records in pdf format how much can i make hosting on vast.ai",
    "s": "payment.mdx"
  },
  {
    "t": "total earnings: this shows your lifetime earnings x74 he total amount you ve earned from all your referrals since you joined the earnings program or started hosting. it includes both paid and unpaid amounts.",
    "s": "earning.mdx"
  },
  {
    "t": "volume offer end dates must align with gpu offer end dates. setting an end date on a volume will not update if there is an existing gpu offer. setting a gpu offer end date will update volume offer end dates.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "allocated storage that is storage in use by client rental contracts is subtracted from the total storage available on a machine and split up proportionally among the machine s gpus in remaining gpu offers.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "> note: if you ve fixed the issue but the system doesn t automatically detect the resolution a vast.ai team member may need to manually check that your machine is functioning correctly and clear the error.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the latest rental end date across all active rental contracts on a machine is shown in the ui. you must keep the machine available until this date. example: multiple rental contracts from different offers",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "paypal paypal issues tax forms to qualifying users directly through their platform. for information on thresholds and delivery refer to paypal s tax help resources. for questions contact paypal support.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "total referral count: this number represents the total users you ve referred x77 ho have successfully created accounts through your referral link. it s a great way to track how your outreach is growing",
    "s": "earning.mdx"
  },
  {
    "t": "there are three ways to access market metrics: dashboards at cloud.vast.ai/host/market/ cli via vastai metrics subcommands requires pip install vastai v1.0.4+ rest api endpoints see api reference below",
    "s": "market-metrics.mdx"
  },
  {
    "t": "your floor price should not be close to your expected actual rental price. the bidding mechanism will bring the price up so you set the minimum you d accept not the price you hope to get. disk pricing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "what it means: the machine passed automated checks for reliability network stability operational health and performance. a verified machine consistently delivers server services to platform standards.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vast.ai does not provide tax documents or tax advice to hosts residing outside the united states. international hosts are responsible for understanding and complying with their local tax obligations.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "you must create a new account for hosting. if you are using vast.ai as a client do not use the same account. a single client and hosting account is not supported and you will quickly run into issues.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "interruptibles work in a bidding system: clients set a bid price for their instance the current highest bid is the instance that runs the others are paused. more info reserved discount pricing factor",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the optimal mix depends on current market conditions so be sure to consider what your competitors are offering and where unmet demand exists. review your utilization patterns and adjust periodically.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "do pass the self-test maintain steady uptime during evaluation. ensure drivers/cuda and networking are correctly installed and reachable. keep the environment clean schedule work via create job only.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "implication: machines aligned with active renter preferences-popular gpus sufficient vram strong reliability fast internet-are prioritized for verification to maximize utilization and profitability.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "the reserved discount pricing is determined by the hosts. if you intend to encourage a long term rental this is a factor that you may want to research. use the filters in the ui to select reserved.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "take the id number from the first column and use that to create a free instance on your own machine. this example loads the latest pytorch image along with both jupyter and ssh direct launch modes.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "from this page you can add or update: company name business address tax identification information other billing details you would like displayed on invoices downloading invoices and payout records",
    "s": "payment.mdx"
  },
  {
    "t": "note: the --ignore-requirements flag runs the test in a relaxed mode bypassing some checks. even if the test passes in this mode your machine does not meet the minimum verification requirements.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "consider enabling the auto-extend feature. this allows rentals to automatically continue beyond their initial term. it reduces churn without requiring you to commit to a longer maximum duration.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "after the payout is submitted your payout provider may require additional processing time before funds appear in your account. why does my invoice show paid when i haven t received the funds yet",
    "s": "payment.mdx"
  },
  {
    "t": "verification is one of the most common filters customers apply when searching. ensuring your machines are verified significantly increases your visibility in search results. data center hosts",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "only machines that meet the platform s reliability and performance thresholds are eligible for verification. there is no manual intervention ensuring consistency scalability and objectivity.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "if you want to use the website gui you will need to setup a new account on a different email address add a credit card and then find your machine and create instances on it like a client.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "your floor price should not be close to your expected actual rental price. the bidding mechanism will bring the price up so you set the minimum you d accept not the price you hope to get.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "when the hosting software detects an error your machine is automatically but temporarily deverified. it will appear as unverified in search results until the underlying issue is resolved.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "if your machine is rejected for not meeting requirements but you still want to check its rentability or run the pressure tests you can rerun the test with the --ignore-requirements flag:",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "duration controls how long a rental contract can last. it s one of the most impactful settings because it affects both the type of customer you attract and the stability of your revenue.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "think of your listing as a product on a shelf. price is only one factor other factors like availability duration terms and configuration determine whether customers even see it. duration",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "ensure you have the latest nvidia drivers installed at the time of listing. outdated drivers can cause compatibility issues with customer workloads and result in failed rentals. testing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "once vast.ai submits the payout to your selected payout provider the invoice status will change to paid. can vast.ai send my payout via direct bank transfer ach swift wire transfer etc.",
    "s": "payment.mdx"
  },
  {
    "t": "click on the 257 cpuram<258 is a decently constrained search that will most likely include a given machine you are looking for that fits these filters amongst others that are similar.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "your listing competes with others for customer attention and your goal is to find the combination of price availability and configuration that maximizes your total revenue over time.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "consider your hardware s relative performance your verification status and your reliability track record as these all affect how customers evaluate your listing against alternatives.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "note: vast.ai is not responsible for delays restrictions compliance reviews account limitations or rejected payments imposed by wise paypal stripe or any other financial institution.",
    "s": "payment.mdx"
  },
  {
    "t": "the paid status reflects the status of the payout within vast.ai s billing system only. it does not indicate whether the funds have completed processing within wise paypal or stripe.",
    "s": "payment.mdx"
  },
  {
    "t": "vms require more disk space than docker containers as they do not share components with the host os. hosts with vms enabled may want to set higher disk and internet bandwidth prices.",
    "s": "vms.mdx"
  },
  {
    "t": "if your network has qos controls or internal metering set a reasonable bandwidth price to prevent any single client from saturating your connection and degrading service for others.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "definition: estimated gpu performance on typical deep-learning tasks e.g. cnn/transformer training for cross-hardware comparison. higher dlperf improves verification odds. read more",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "do verify gpu pcie connections provide full bandwidth and are not throttled. keep the latest drivers/cuda aligned with workloads. confirm required ports and end-to-end reachability.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "this process may take some time as the system ensures that the issue is fully resolved before restoring verification. most error messages are cleared within 1-2 hours of resolution.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "read through this documentation to understand the minimum requirements for becoming a datacenter partner and the specific verification steps that we will take to ensure compliance.",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "current balance: this is the amount you ve earned so far from your referred users but haven t been paid out yet. x49 t keeps growing as your referrals continue to use the platform.",
    "s": "earning.mdx"
  },
  {
    "t": "hosts are responsible for: setup: installing ubuntu creating disk partitions installing nvidia drivers opening network ports on the router and installing the vast hosting software.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if you have confirmed your payout account is in good standing and still have not received your funds after a reasonable processing period please contact support for further review.",
    "s": "payment.mdx"
  },
  {
    "t": "how should i begin fixing it a red error indicator will appear on your machine in the machines tab. use this message to identify and investigate the issue in your logs or metrics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "do investigate red error indicators quickly review logs and metrics. validate thermal/power headroom and bandwidth under load. re-check health after changes to confirm resolution.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "we will need to ensure iommu a technology that secures and isolates communication between pcie devices is set up along with disabling all driver features that interfere with vms.",
    "s": "vms.mdx"
  },
  {
    "t": "the rental contract locks in all of the offer s terms at the time of rental including pricing the rental end date and hardware specs and those terms cannot be changed afterward.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "think of your listing as a product on a shelf. price is only one factor other factors like availability duration terms and configuration determine whether customers even see it.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "ensure you have the latest nvidia drivers installed at the time of listing. outdated drivers can cause compatibility issues with customer workloads and result in failed rentals.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "when a client rents an instance from your offer all of the offer s terms at that moment the offer end date the pricing and the hardware specs are locked into a rental contract.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "data center hosts: do not set a duration longer than you can reliably honor. breaking a contract early carries a serious penalty. only commit to what you can guarantee. pricing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "note that default configuration settings for most machines will not support vms and we can detect that so most hosts who do not want vms enabled do not need to take any action.",
    "s": "vms.mdx"
  },
  {
    "t": "settings alone won t help if your machines aren t reliable and up to date. a few operational basics make a significant difference in your listing s performance. driver updates",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the paid status only reflects the payout status within vast.ai s billing system. it does not indicate whether the funds have completed processing within wise paypal or stripe.",
    "s": "payment.mdx"
  },
  {
    "t": "to generate an invoice: you must have a valid payout method connected to your vast.ai account. your account balance must meet the 20 minimum payout threshold. payment timeline",
    "s": "payment.mdx"
  },
  {
    "t": "on new machines the tests will be run on install for machines configured before the vm-feature release testing for vm-compatability will happen when the machine is unoccupied.",
    "s": "vms.mdx"
  },
  {
    "t": "the on-demand price is the price per hour for the gpu rental. on demand rentals are the highest priority and if met will stop interruptibles. interruptible min price optional",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the space allocated for volume offers is in the same pool of space as that for gpu offers meaning that space will not be subtracted from available offers unless it is in use.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this guide explains how vast.ai host payouts work when invoices are generated when payments are sent and what to do if you experience a payout issue. available payout methods",
    "s": "payment.mdx"
  },
  {
    "t": "verification is one of the most common filters customers apply when searching. ensuring your machines are verified significantly increases your visibility in search results.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "conversely all-8x can work if competitors in your gpu class are highly fragmented and there s strong demand for full nodes but it s generally not the default recommendation.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "vm support will allow your machine to take advantage of demand for use cases that docker cannot easily support in addition to demand for conventional docker-based instances.",
    "s": "vms.mdx"
  },
  {
    "t": "equipment that is in a certified datacenter on vast.ai is eligible to be included in the secure cloud offering and receive other benefits such as the blue datacenter label.",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "if your machine has multiple gpus and you ve set mingpu to allow slicing multiple clients can rent from the same offer each creating their own independent rental contract.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "each rental contract is independent you may have multiple active rental contracts from different clients on the same machine each with its own rental end date and pricing.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "each endpoint allows up to 5 requests per second per user. for large historical queries the backend automatically adjusts the resolution to keep response sizes reasonable.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "ensure that your internet power source and heat dissipation systems are all functioning and that you have thought through how hosting will affect each one of those items.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "parameter applies to description --- --- --- verified current history yes no or all hostingtype current history securecloud community or all gpuname history gpu name e.g.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "open /etc/default/grub and add to the grubcmdlinelinux the following: amdiommu on or inteliommu on depending on whether you have an amd or intel cpu. nvidiadrm.modeset 0",
    "s": "vms.mdx"
  },
  {
    "t": "data center hosts: do not set a duration longer than you can reliably honor. breaking a contract early carries a serious penalty. only commit to what you can guarantee.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "if stored instances are only taking up 400 gb the volume offer will not update as there is still enough space on the machine to cover the volume offer. listing volumes",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "invoices are generated weekly on fridays. once an invoice is generated it enters a pending state and is scheduled for payment during the following friday payout cycle.",
    "s": "payment.mdx"
  },
  {
    "t": "we will check/test your configuration when your machine is idle and enable vms by default if your machine is capable of supporting vms and you have not set vms to off.",
    "s": "vms.mdx"
  },
  {
    "t": "machines that do not have vm support enabled will be hidden in the search page for clients who have vm-based templates selected. vm support benefits/drawbacks benefits",
    "s": "vms.mdx"
  },
  {
    "t": "you can generate earnings by gaining vast credit through template creation via our referral program. you can find more information about vast s referral program here.",
    "s": "earning.mdx"
  },
  {
    "t": "interruptibles work in a bidding system: clients set a bid price for their instance the current highest bid is the instance that runs the others are paused. more info",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "to qualify a machine must pass minimum baseline and health/stability checks. beyond that the system evaluates four primary criteria order not indicative of priority :",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "total earnings: this shows your lifetime earnings x74 he total amount you ve earned from all your referrals since you joined the earnings program or started hosting.",
    "s": "earning.mdx"
  },
  {
    "t": "vm support is currently an optional feature for hosts as it usually requires additional configuration steps on top of those needed to support docker-based instances.",
    "s": "vms.mdx"
  },
  {
    "t": "managing your offers including pricing and offer end dates planning maintenance so that no active rental contracts are disrupted account setup and hosting agreement",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you must be signed in as a host with at least one registered machine to access this page. alternatively check out gpu market prices or the host earnings calculator.",
    "s": "payment.mdx"
  },
  {
    "t": "verification is entirely automated by proprietary algorithms that assess each machine s operational health and performance incorporating supply-and-demand dynamics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "tip: meeting these minimum requirements makes your machine eligible for verification but does not automatically guarantee verification. read more about verification",
    "s": "verification-stages.mdx"
  },
  {
    "t": "we also generally recommend multi-gpu hosts with rtx 40x0 series gpus try enabling vms especially if they have plentiful disk space and fast 500mbps+ internet speed",
    "s": "vms.mdx"
  },
  {
    "t": "for windows users we suggest setting up wsl which will require you to install ubuntu on your windows machine and change your bios settings to allow virtualization.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "host machines are not required to be vm compatible the vast hosting software will automatically test and enable the feature on machines on which vms are supported.",
    "s": "vms.mdx"
  },
  {
    "t": "you can set the offer end date in the hosting interface by clicking on the date field under expiration or via the end date field in the cli list machine command.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "we do not recommend multi-gpu hosts with datacenter gpus enable vms until we can ensure better gpu p2p communication support in vms including support for nvlink.",
    "s": "vms.mdx"
  },
  {
    "t": "settings alone won t help if your machines aren t reliable and up to date. a few operational basics make a significant difference in your listing s performance.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this page in the console allows you to manage your earnings from referrals. you can find more information about vast s referral program here. pages walkthrough",
    "s": "earning.mdx"
  },
  {
    "t": "please verify that your payout method has been connected correctly in your account settings. can i generate an invoice manually customizing invoice information",
    "s": "payment.mdx"
  },
  {
    "t": "if you operate multiple machines distribute your min gpu settings across them rather than using the same value everywhere. a healthy mix might look like this:",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "if they create a volume offer of 500 gb and it is not rented the machine will be available for rent with 2 offers of 1xgpu 500gb and 1 offer of 2xgpu 1000gb.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "note: meeting these minimum requirements makes your machine eligible for verification but does not automatically guarantee verification. about the self-test",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "if you are an international host receiving payouts via wise please refer to the international hosts section above. common questions does vast.ai handle vat",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "do monitor health uptime thermals power and respond to alerts. keep drivers/cuda on compatible latest stable versions. maintain stable symmetric bandwidth.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "once verified a machine will remain verified unless issues arise such as failing health checks or reliability standards which could lead to deverification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "currently no other peer-to-peer gpu rental marketplace offers full vms instead full vms are only available from traditional providers at much higher costs.",
    "s": "vms.mdx"
  },
  {
    "t": "market data suggests there is meaningful demand for both 1x and 8x configurations with approximately twice as much search volume for 8x rentals as for 1x.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "setup: installing ubuntu creating disk partitions installing nvidia drivers opening network ports on the router and installing the vast hosting software.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this will automatically remove expired/deleted rental contracts from the machine and available storage will update on offers. extending rental contracts",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a machine that appears available but fails when rented wastes a customer s time and yours so you lose the rental and risk a negative reliability signal.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "hosts are responsible for ensuring they can receive business-to-business b2b payments through their selected payout provider in their country or region.",
    "s": "payment.mdx"
  },
  {
    "t": "10-series nvidia gpu or mi25 or newer radeon instinct series gpu or radeon vii or radeon pro vii or radeon rx 7900 gre/xt/xtx or radeon pro w7900/w7800.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "if stored instances are only taking up 400 gb the volume offer will not update as there is still enough space on the machine to cover the volume offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "note: meeting the minimum requirements makes your machine eligible for verification but it does not guarantee that verification will occur immediately.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "tip: ensure no other jobs or instances are running during the self-test for the most accurate results. step-by-step guide step 0: install the vast cli",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "a red error indicator will appear on your machine in the machines tab. use this message to identify and investigate the issue in your logs or metrics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "this guide explains how vast.ai host payouts work when invoices are generated when payments are sent and what to do if you experience a payout issue.",
    "s": "payment.mdx"
  },
  {
    "t": "host earnings depend on several factors including: hardware specifications pricing uptime and reliability geographic location current customer demand",
    "s": "payment.mdx"
  },
  {
    "t": "if you have vms set to off and you d like to retry enabling vms run sudo python3 /var/lib/vastaikaalia/enablevms.py on -f while your machine is idle.",
    "s": "vms.mdx"
  },
  {
    "t": "individual certifications will eventually be highlighted so users can understand if a given host is compliant with hipaa gdpr tier 2/3 or iso 27001.",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "wise if you are a us-based host receiving payouts via wise vast.ai is required to collect your tax information directly. please submit your w9 here:",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "to prevent vms from being enabled on your machine or to disable vms after they have been enabled run python3 /var/lib/vastaikaalia/enablevms.py off.",
    "s": "vms.mdx"
  },
  {
    "t": "the latest rental end date across all active rental contracts on a machine is shown in the ui. you must keep the machine available until this date.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this discount is not static but rather scales over time that the user rents the machine for. these values are determined by the individual host s .",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "to extend the current rental contracts for all clients on a given machine change the offer end date to a later time with the same or lower pricing.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "funds are then processed by wise paypal or stripe and may take additional time to appear in your account depending on the provider and your region.",
    "s": "payment.mdx"
  },
  {
    "t": "total referral count: this number represents the total users you ve referred x77 ho have successfully created accounts through your referral link.",
    "s": "earning.mdx"
  },
  {
    "t": "hosts can create offers sometimes called listings through the cli command list machine or the machine control panel gui on the host machines page.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "once created a rental contract s terms cannot be changed not by modifying the offer not by unlisting the machine and not by any other host action.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if you operate out of a data center consider highlighting any certifications you hold e.g. tier 4 data center hipaa compliance as differentiators.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "disclaimer: as an independent contractor you are solely responsible for tracking your earnings and accurately reporting them in your tax filings.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "invoices are only generated when: a payout method is connected to your vast.ai account. your balance has reached the 20 minimum payout threshold.",
    "s": "payment.mdx"
  },
  {
    "t": "on february 1 client b rents the other 2 gpus from the new offer. a rental contract is created at 2.50/gpu/hr with a rental end date of june 30.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "to rent your own machine you will need to first search the offers with your machine id to find the id and then create an instance using that id.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the earnings x70 age gives you a transparent view of your referral program performance and accumulated rewards. here s what each section means:",
    "s": "earning.mdx"
  },
  {
    "t": "depending on your payout method your payment provider may issue a tax form if you meet their reporting threshold. it is your responsibility to:",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "recovery: fix the issue and restore stability the system will automatically transition back to verified once system confirms healthy operation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "this page in the console allows you to manage your earnings from referrals. you can find more information about vast s referral program here.",
    "s": "earning.mdx"
  },
  {
    "t": "the on-demand price is the price per hour for the gpu rental. on demand rentals are the highest priority and if met will stop interruptibles.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "once clients rent your machine it is very important to honor the terms of each rental contract until its rental end date. the rental contract",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "connect your vast host account to our discord to access our host-only discord channels to chat or seek help from other hosts on the platform.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the optimal mix depends on current market conditions so be sure to consider what your competitors are offering and where unmet demand exists.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "check that virtualization is enabled in your bios. on most machines this should be enabled by default. configure kernel commandline arguments",
    "s": "vms.mdx"
  },
  {
    "t": "the host must have at least 5 gpu servers listed on vast.ai or otherwise show they have a significant 5+ servers amount of equipment to list",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "rtx 4090 start history unix timestamp for range start end history unix timestamp for range end step history seconds between data points e.g.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "total rental earnings host only : x54 his shows the total lifetime amount you ve earned from your machine being rented out on the platform.",
    "s": "earning.mdx"
  },
  {
    "t": "keep in mind our auto sort that search offers defaults to is comprised of both ranking various factors as well as an element of randomness.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "different customer types have very different duration preferences. understanding this helps you target the right segment for your hardware:",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "set disk pricing higher than you might expect. this prevents stopped instances from consuming all your storage and starving active rentals.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "short duration to long duration :-- :-: --: flexibility lower commitment higher expected value price lock-in customer segments by duration",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "you may not run any background gpu processes for vms to work nvidia-persitenced is ok it is managed by our hosting software . enabling vms",
    "s": "vms.mdx"
  },
  {
    "t": "on january 20 you decide to raise the price. you unlist the current offer and relist at 2.50/gpu/hr with a new offer end date of june 30.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "once you are ready to list your machine come back to this guide to understand pricing and the rental contract lifecycle. general concepts",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the offer end date becomes the contract s rental end date shown in the ui as client end date and the pricing becomes the contract s rate.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "customer type typical duration need notes :-- :-- :-- serverless / automated inference short hours to days these workloads are transient.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "note: meeting these minimum requirements makes your machine eligible for verification but does not automatically guarantee verification.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "reserved instance discounts are a feature for clients which allows them to rent machines over a long period of time at a reduced price.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "market metrics data is updated every 5 minutes. location data is cached for up to 2 hours since it changes less frequently. rate limits",
    "s": "market-metrics.mdx"
  },
  {
    "t": "tip: meeting these minimum requirements makes your machine eligible for verification but does not automatically guarantee verification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "unlisting the machine prevents new rental contracts entirely but existing ones continue at their original pricing and rental end dates",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "when you set a min gpu value the platform creates listings at all powers of two from your minimum up to the total gpus in the machine.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "do offer in-demand gpu models with adequate vram and balanced resources. maintain strong reliability to remain attractive once listed.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "what it means: a previously verified machine no longer meets requirements. system continuous monitoring detects sustained degradation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "other 6000 series or newer radeon rx/pro w series gpus may be supported but may not be searchable using standard filters for amd rocm.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "important: even with --ignore-requirements your machine must have at least three direct open ports otherwise the self-test will fail.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "fix the issue and restore stability the system will automatically transition back to verified once system confirms healthy operation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "avoid downgrading hardware capacity e.g. reducing gpu count disk or ram . allowing thermal power or bandwidth instability under load.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "either you disabled vms or our previous tests failed. pending: vms are not disabled but will try to enable once the machine is idle.",
    "s": "vms.mdx"
  },
  {
    "t": "it s one of the most impactful settings because it affects both the type of customer you attract and the stability of your revenue.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "if you have fast unmetered upstream internet you can price bandwidth low or even at zero as this is a strong competitive advantage.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this guide covers the configuration steps needed to enable support for vast vms on most setups but is not and cannot be exhausitve.",
    "s": "vms.mdx"
  },
  {
    "t": "price is only one factor other factors like availability duration terms and configuration determine whether customers even see it.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "please refer to your payout provider s documentation for regional availability account requirements and verification requirements.",
    "s": "payment.mdx"
  },
  {
    "t": "after a payout has been submitted your payout provider may require additional processing time before funds appear in your account.",
    "s": "payment.mdx"
  },
  {
    "t": "> note: higher reliability greatly improves verification likelihood. sustained 99.99% up to 99.9999%+ uptime is typically favored.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "you can view your payout history for a selected date range. here you can generate and download invoices for your earning payouts.",
    "s": "earning.mdx"
  },
  {
    "t": "machine min gpu available listings :-- :-- :-- machine a 1 1x 2x 4x 8x machine b 2 2x 4x 8x machine c 4 4x 8x machine d 8 8x only",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "definition: estimated gpu performance on typical deep-learning tasks e.g. cnn/transformer training for cross-hardware comparison.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "users typically are willing to pay more for the security and reliability that comes with equipment that is in a proper facility.",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the core tradeoff: smaller minimums e.g. 1x let you serve more customers and fill individual gpu slots but create fragmentation.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "machines that do not have vm support enabled will be hidden in the search page for clients who have vm-based templates selected.",
    "s": "vms.mdx"
  },
  {
    "t": "the min gpu field allows you to set the smallest grouping of gpu rentals available on your machine in powers of 2 or down to 1.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "by default volume offers will be listed with gpu offers at the same disk price for half of the available space on the machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "after the payout is submitted your payout provider may require additional processing time before funds appear in your account.",
    "s": "payment.mdx"
  },
  {
    "t": "direct bank transfers ach payments wire transfers and swift payments are not available. my account is not generating invoices.",
    "s": "payment.mdx"
  },
  {
    "t": "this will automatically remove expired/deleted rental contracts from the machine and available storage will update on offers.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can use this data to make informed decisions about pricing your machines and understanding demand for specific gpu types.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "once an invoice is generated it enters a pending state and is scheduled for payment during the following friday payout cycle.",
    "s": "payment.mdx"
  },
  {
    "t": "we recommend all hosts with single-gpu rigs to try to ensure vm support as the drawbacks for single-gpu machines are minimal.",
    "s": "vms.mdx"
  },
  {
    "t": "you may not run any background gpu processes for vms to work nvidia-persitenced is ok it is managed by our hosting software .",
    "s": "vms.mdx"
  },
  {
    "t": "shortening the offer end date limits the commitment window for new clients but does not shorten any existing rental end date",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vast provides real-time and historical data on gpu supply demand pricing and geographic distribution across the marketplace.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "this guide covers the economic decisions that is the settings and strategies that affect your ranking occupancy and revenue.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "it automatically evaluates key system aspects and simulates real workloads to validate both hardware and network readiness.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "market metrics data is updated every 5 minutes. location data is cached for up to 2 hours since it changes less frequently.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "the core tradeoff: longer durations tend to increase expected earnings because customers value the guaranteed availability.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the host setup guide is the official documentation for setting up a machine on vast.ai. read through each section closely.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "it is vital to test your own machine to ensure the ports and software is running smoothly. setup a separate client account",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai metrics gpu all gpu types vastai metrics gpu --verified true --datacenter true vastai metrics gpu --raw json output",
    "s": "market-metrics.mdx"
  },
  {
    "t": "if you operate multiple machines distribute your min gpu settings across them rather than using the same value everywhere.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "once clients rent your machine it is very important to honor the terms of each rental contract until its rental end date.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "customers filter and sort listings by a variety of criteria most commonly by verification status duration and disk space.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "if your listing doesn t pass these filters it won t appear in search results regardless of how competitive your price is.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "internet download speed must scale with total machine vram at 2.6 mbps per gib with a 100 mbps floor and 500 mbps ceiling",
    "s": "verification-stages.mdx"
  },
  {
    "t": "wise if you are a us-based host receiving payouts via wise vast.ai is required to collect your tax information directly.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "once you are ready to list your machine come back to this guide to understand pricing and the rental contract lifecycle.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this process involves no manual intervention ensuring consistent scalable and objective verification across all systems.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "what it means: the machine passed automated checks for reliability network stability operational health and performance.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "this prevents stopped instances from consuming all your storage and starving active rentals. internet bandwidth pricing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "definition: ongoing evaluation of market trends and renter behavior to surface configurations most likely to be rented.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "internet upload speed must scale with total machine vram at 2.6 mbps per gib with a 100 mbps floor and 500 mbps ceiling",
    "s": "verification-stages.mdx"
  },
  {
    "t": "a previously verified machine no longer meets requirements. system continuous monitoring detects sustained degradation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "in the payout account section you can set up a payout account. common questions how can i have earnings as a vast user",
    "s": "earning.mdx"
  },
  {
    "t": "gpu: type memory and count matter. newer datacenter/workstation gpus are prioritized e.g. b200 > h200 >> 5090 > 4070 .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "testing and troubleshooting all issues that can arise such as driver conflicts errors bad gpus and bad network ports.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "do use the latest compatible drivers/cuda. eliminate pcie thermal and power bottlenecks to maintain sustained clocks.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "this process may take some time as the system ensures that the issue is fully resolved before restoring verification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vast now supports vm instances running on kernel virtual machine kvm in addition to docker container based instances.",
    "s": "vms.mdx"
  },
  {
    "t": "for example on a machine with 1000gb of disk available and 2 gpus a host can create a volume offer of up to 1000 gb.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if 200 gb of the volume offer are rented the gpu offers will reduce to 2 1xgpu 400gb offers and 1 2xgpu 800gb offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "only machines that meet the platform s defined reliability and performance thresholds are eligible for verification.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "on january 5 client a rents 2 gpus. a rental contract is created at 2.00/gpu/hr with a rental end date of march 31.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if the test fails: the cli will display detailed reasons for failure. apply the suggested fixes and rerun the test.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "if you are an international host receiving payouts via wise please refer to the international hosts section above.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "new rental contracts will be created at the new terms while old rental contracts continue at their original terms.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the reserved discount pricing factor represents the maximum possible discount a user can achieve on your machines.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "when a client rents a volume offer they rent a subset of the total space set for the offer up to the total amount.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the self-test helps confirm that your machine satisfies vast.ai s minimum performance and configuration standards.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "before running the test make sure: your machine has been listed. there are no active clients currently renting it.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "returns time-series data for supply demand and pricing. defaults to rtx 5090 4090 and 3090 over the last 24 hours.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "as rendering/gaming users will benefit from those as well as users who need multi-application orchestration tools.",
    "s": "vms.mdx"
  },
  {
    "t": "depending on your payout method your payment provider may issue a tax form if you meet their reporting threshold.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "min gpu 1 to min gpu 8 :-- :-: --: more renters more fragmentation fewer renters cleaner utilization how it works",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "it s the product of your price per hour and your occupancy rate the percentage of time your machines are rented .",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "avoid pairing high-end gpus with under-provisioned cpu/ram. letting hidden background services consume resources.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "volume offers will be unlisted when the machine is unlisted. they can additionally be unlisted with the command:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "./vastai create instance --image pytorch/pytorch:latest --jupyter --direct --env -e tz pdt -p 22:22 -p 8080:8080",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this means a single machine may have active rental contracts at different prices and different rental end dates.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you now have two active rental contracts on the same machine at different prices and different rental end dates.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can control the amount of space listed with the -v cli option and the price of the space with the -z option.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "for large historical queries the backend automatically adjusts the resolution to keep response sizes reasonable.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "the bidding mechanism will bring the price up so you set the minimum you d accept not the price you hope to get.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "storage is not your bottleneck. you are under-provisioned on disk set disk pricing higher than you might expect.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "balances below 20 usd will automatically roll forward until the minimum threshold is reached. invoice generation",
    "s": "payment.mdx"
  },
  {
    "t": "total referral earnings host only : this shows the total lifetime amount you ve earned from all your referrals.",
    "s": "earning.mdx"
  },
  {
    "t": "the earnings x70 age gives you a transparent view of your referral program performance and accumulated rewards.",
    "s": "earning.mdx"
  },
  {
    "t": "additionally there is the earning chart section that provides a clear visual overview of your earning history.",
    "s": "earning.mdx"
  },
  {
    "t": "make sure to test the networking. clients require open ports to directly connect to the machine for most jobs.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if the test says the machine is not found or not rentable : try un-listing your machine then listing it again.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "who this is for: hosts who have already completed the technical setup process and have machines ready to list.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "avoid ignoring warnings or allowing instability to persist. reducing hardware below the created specification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "some hosts may also need to add the following settings: rd.driver.blacklist nouveau modprobe.blacklist nouveau",
    "s": "vms.mdx"
  },
  {
    "t": "only rented space will impact the amount of space available for gpu offers not the space in the offer itself.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if for some reason this is not working or if you want to free the space automatically you can run the command",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can then look at your instance tab to make sure that pytorch loaded correctly along with jupyter and ssh.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "verification confirms that your machine is stable performant and properly configured to run client workloads.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "ensure your machine has no missing data in your machines page such as upload and download speed ram or ports.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "only machines that meet the platform s reliability and performance thresholds are eligible for verification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vast.ai cannot provide tax advice and we cannot verify the accuracy of any publicly available tax guidance.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "before your machine can be verified on vast.ai it must meet all minimum quality and reliability benchmarks.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "for example on an 8-gpu machine with min gpu set to 2 listings are created for 2x 4x and 8x configurations.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "avoid unnecessary reboots or configuration changes. unrelated background workloads that consume gpu/cpu/io.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the name and address of the datacenter where the equipment is located along with the relevant certificates",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the discount schedule param which determines the price difference between on-demand and reserved instances",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "make sure to set an offer end date before listing your machine or the offer will remain open indefinitely.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "larger minimums e.g. 8x eliminate fragmentation but limit your audience to customers who need a full node.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this approach lets you capture demand across all configuration sizes while keeping fragmentation in check.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "yes but changes only affect future rental contracts. existing rental contracts keep their original terms:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "gpu count: for the same gpu type more gpus increase verification likelihood e.g. 85090 >> 25090 > 15090 .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "system optimization upgrades balanced scaling matters cpu/ram/pcie/bandwidth commensurate with gpu tier .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "in order for your unverified machine to be verified it must also meet the following minimum requirements:",
    "s": "verification-stages.mdx"
  },
  {
    "t": "lifecycle: machines automatically move between these states based on performance and reliability factors.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the offer end date is your commitment to how long you will keep the machine online and fully functional.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "for example if you have an 8x 3090 and set min gpu to 2 clients can create instances with 2 4 or 8 gpus.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the interruptible price allows for the host to set the minimum interruptible price for a client to rent.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the website gui stacks similar offers and so it is not easy to see all the listings for a given machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "situation approach :-- :-- you have excess disk capacity set disk pricing closer to your amortized cost.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "once vast.ai submits the payout to your selected payout provider the invoice status will change to paid.",
    "s": "payment.mdx"
  },
  {
    "t": "if you have a display manager e.g. gdm or display server xorg wayland etc running you must disable them.",
    "s": "vms.mdx"
  },
  {
    "t": "similarly if stored instances on the machine are taking up 800gb the volume offer will reduce to 200gb.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if you have raised the pricing you cannot extend the current rental contracts. testing your own machine",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "follow the official setup guide to install the vast cli: vast cli: get started step 1: set your api key",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "avoid setting all machines to 1x as this leads to severe fragmentation and reduced overall utilization.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "testing the recommended pytorch template is vital to ensure that ssh and jupyter are working properly.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "tip: ensure no other jobs or instances are running during the self-test for the most accurate results.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "even if the test passes in this mode your machine does not meet the minimum verification requirements.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "before tuning any individual setting it helps to understand where your supply sits relative to demand.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "check that virtualization is enabled in your bios. on most machines this should be enabled by default.",
    "s": "vms.mdx"
  },
  {
    "t": "international hosts are responsible for understanding and complying with their local tax obligations.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "as a host you can set this number yourself to 0 if you wish to opt out of this feature. volume offers",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the original vs. the updated price will be shown as denoted by a stikethrough in the original amount:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "outdated drivers can cause compatibility issues with customer workloads and result in failed rentals.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "blue datacenter label on all gpu offers in the web interface for equipment that is in the datacenter",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "you can generate earnings by gaining vast credit through template creation via our referral program.",
    "s": "earning.mdx"
  },
  {
    "t": "vast.ai is based in california and does not currently collect or remit vat. is vat shown on invoices",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "make sure to disable auto-updates so that your machine doesn t drop a client job to update a driver.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "take the id number from the first column and use that to create a free instance on your own machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "recommended strategy: set your min bid price close to your cost of power when the gpu is under load.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "an invoice is marked as paid once vast.ai has submitted the payout to your selected payout provider.",
    "s": "payment.mdx"
  },
  {
    "t": "pcie bandwidth: adequate throughput is essential bottlenecks depress dlperf and overall performance.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "when the hosting software detects an error your machine is automatically but temporarily deverified.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vms require more disk space than docker containers as they do not share components with the host os.",
    "s": "vms.mdx"
  },
  {
    "t": "a high price with low occupancy can easily earn less than a moderate price with strong utilization.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "invoices are generated every friday and are generally scheduled to be paid on the following friday.",
    "s": "payment.mdx"
  },
  {
    "t": "definition: stable uninterrupted operation over time uptime resilience under continuous workloads .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "vast is a gpu marketplace. hosts sell gpu resources on the marketplace. hosts are responsible for:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "lower price to higher price :-- :-: --: higher occupancy higher per-hour revenue on-demand pricing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "many hosts set their interruptible floor too high because they treat it like their on-demand rate.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "avoid frequent restarts or unplanned outages. overheating undervolting or unstable power delivery.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "vast.ai does not provide tax documents or tax advice to hosts residing outside the united states.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the paid status indicates that vast.ai has submitted the payout to your selected payout provider.",
    "s": "payment.mdx"
  },
  {
    "t": "possible results are: on: vms are enabled on your machine. off: vms are disabled on your machine.",
    "s": "vms.mdx"
  },
  {
    "t": "contact your payment provider directly with any questions about your tax forms. by payout method",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "you will notice there is now a link to machines in the navigation along with some other changes.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this example loads the latest pytorch image along with both jupyter and ssh direct launch modes.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can also query the data directly via the rest api. pass your host api key as a bearer token.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "customers bid above this floor and competition among bidders will drive the actual price higher.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "bidders will typically pay above this floor so your actual interruptible revenue will be higher.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the volume offer will still remain as there is still available space and update to offer 300gb.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a pending invoice has been generated and is scheduled for payment during the next payout cycle.",
    "s": "payment.mdx"
  },
  {
    "t": "the latest rental end date across all active rental contracts on a machine is shown in the ui.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you must keep the machine online and fully functional through june 30 to honor both contracts.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "ensuring your machines are verified significantly increases your visibility in search results.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "it does not indicate whether the funds have completed processing within wise paypal or stripe.",
    "s": "payment.mdx"
  },
  {
    "t": "to generate an invoice: you must have a valid payout method connected to your vast.ai account.",
    "s": "payment.mdx"
  },
  {
    "t": "when a client rents an instance on your machine a rental contract is created from your offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if you intend to encourage a long term rental this is a factor that you may want to research.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "balances below 20 usd will automatically roll forward until the minimum threshold is reached.",
    "s": "payment.mdx"
  },
  {
    "t": "invoices generated on friday are generally scheduled to be paid on the following friday. paid",
    "s": "payment.mdx"
  },
  {
    "t": "software drivers/cuda must be correctly installed and compatible use stable latest releases .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "thus we believe that hosts who have vms enabled can expect to command a substantial preumium.",
    "s": "vms.mdx"
  },
  {
    "t": "log in to stripe express to confirm your tax information name address ssn or ein is current.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "you unlist the current offer and relist at 2.50/gpu/hr with a new offer end date of june 30.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this discount is not static but rather scales over time that the user rents the machine for.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a well-set interruptible floor ensures your gpus are working even during low-demand periods.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this prevents stopped instances from consuming all your storage and starving active rentals.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "please verify that your payout method has been connected correctly in your account settings.",
    "s": "payment.mdx"
  },
  {
    "t": "off: vms are disabled on your machine. either you disabled vms or our previous tests failed.",
    "s": "vms.mdx"
  },
  {
    "t": "note: the --ignore-requirements flag runs the test in a relaxed mode bypassing some checks.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "availability pricing - historical supply/demand counts and p10/median/p90 pricing over time",
    "s": "market-metrics.mdx"
  },
  {
    "t": "it is vital to test your own machine to ensure the ports and software is running smoothly.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a single client and hosting account is not supported and you will quickly run into issues.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a rental contract is created each time a client accepts your offer by renting an instance.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a volume offer is an offer for storage space and can be priced separately from gpu offers.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "all three require a host api key. regular client keys will receive a 401 error. dashboards",
    "s": "market-metrics.mdx"
  },
  {
    "t": "for an 8-gpu machine this determines whether customers can rent 1 2 4 or 8 gpus at a time.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "before contacting support please verify: your payout account is active and fully verified.",
    "s": "payment.mdx"
  },
  {
    "t": "--- host responsibilities always keep systems stable well-cooled and correctly configured.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "if the machine is offline at this time there is a job that runs hourly to free the space.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "these can be meaningful selling points for enterprise and compliance-sensitive customers.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "you must be signed in as a host with at least one registered machine to access this page.",
    "s": "payment.mdx"
  },
  {
    "t": "do not reduce hardware after creation e.g. fewer gpus/ram - this will trigger deverified.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "beyond that the system evaluates four primary criteria order not indicative of priority :",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "the client s data must be isolated and protected according to the data protection policy",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if no one bids consider running your own background jobs on the otherwise-idle hardware.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "invoices generated on friday are generally scheduled to be paid on the following friday.",
    "s": "payment.mdx"
  },
  {
    "t": "to understand current market pricing and utilization trends visit the market stats page.",
    "s": "payment.mdx"
  },
  {
    "t": "then run sudo update-grub and reboot. disable display managers/background gpu processes.",
    "s": "vms.mdx"
  },
  {
    "t": "as a host you can set this number yourself to 0 if you wish to opt out of this feature.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the host setup guide is the official documentation for setting up a machine on vast.ai.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "expect that the gpu is going to be used at close to max capacity for the rental period.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai metrics gpu-locations --verified true --datacenter true datacenter-verified only",
    "s": "market-metrics.mdx"
  },
  {
    "t": "the core tradeoff: higher prices increase revenue per rental hour but reduce occupancy.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "direct bank transfers ach payments wire transfers and swift payments are not available.",
    "s": "payment.mdx"
  },
  {
    "t": "the paid status reflects the status of the payout within vast.ai s billing system only.",
    "s": "payment.mdx"
  },
  {
    "t": "before selecting a payout method verify that: the service is available in your country.",
    "s": "payment.mdx"
  },
  {
    "t": "invoices are only generated when: a payout method is connected to your vast.ai account.",
    "s": "payment.mdx"
  },
  {
    "t": "multi-application server tooling and devops e.g. docker compose kubernetes docker build",
    "s": "vms.mdx"
  },
  {
    "t": "you can also directly create a volume offer by running the vastai list volume command.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "once that filter is selected hosts who offer that discount will become easily visible.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can see the number of available listings as well as information about the machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "customers often prefer very long durations or no maximum. stable high-value contracts.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "upgrades adding gpus/ram are allowed but may take time to reflect across the platform.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "it will appear as unverified in search results until the underlying issue is resolved.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "you will require a cpu and a chipset that support intel vt-d or amd-vi. configure bios",
    "s": "vms.mdx"
  },
  {
    "t": "the owners of the business must be listed on the registration or otherwise verifiable",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the advertised services must be provided until each rental contract s rental end date",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can also unlist and relist with entirely new terms new price new offer end date .",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a few operational basics make a significant difference in your listing s performance.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "storage: both capacity and bandwidth e.g. nvme impact responsiveness and reliability.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "offers are included in the secure cloud searches in the cli and in the web interface",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the template performance chart displays the earnings history from templates. payouts",
    "s": "earning.mdx"
  },
  {
    "t": "drivers/cuda must be correctly installed and compatible use stable latest releases .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "if you have questions about your tax obligations please consult a tax professional.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "paypal paypal issues tax forms to qualifying users directly through their platform.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the offer end date which determines how long the offer accepts new rental contracts",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "as the host you are committing to provide the services as advertised in your offer:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "newer datacenter/workstation gpus are prioritized e.g. b200 > h200 >> 5090 > 4070 .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "business information such as a certificate of good standing or other recent record",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "setting an end date on a volume will not update if there is an existing gpu offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai metrics gpu-trends rtx 4090 --start 1773298800 --end 1773817200 --step 3600",
    "s": "market-metrics.mdx"
  },
  {
    "t": "at this floor you re at least covering your electricity costs during idle periods.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "it s a critical lever for balancing demand capture against utilization efficiency.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "definition: hardware network and software readiness to meet operational standards.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "virtualization enabling vm support significantly improves verification likelihood.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "in order to be listed on vast.ai the machine must follow these minimum guidelines:",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the host must provide the hardware/services according to all the advertised specs",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "dedicated machines only - the machine shouldn t be doing other stuff while rented",
    "s": "verification-stages.mdx"
  },
  {
    "t": "there is no manual intervention ensuring consistency scalability and objectivity.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "hosts with vms enabled may want to set higher disk and internet bandwidth prices.",
    "s": "vms.mdx"
  },
  {
    "t": "as a result of a few factors generally higher search rankings in the marketplace",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "for information on thresholds and delivery refer to paypal s tax help resources.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "disk pricing depends on how much storage you have relative to what clients need:",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "partial rentals can leave awkward hard-to-fill gaps leading to underutilization.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "your account must accumulate at least 20 usd before an invoice can be generated.",
    "s": "payment.mdx"
  },
  {
    "t": "can vast.ai send my payout via direct bank transfer ach swift wire transfer etc.",
    "s": "payment.mdx"
  },
  {
    "t": "the paid status only reflects the payout status within vast.ai s billing system.",
    "s": "payment.mdx"
  },
  {
    "t": "vms support the following features/use-cases that docker-based instances do not:",
    "s": "vms.mdx"
  },
  {
    "t": "contact your payment provider directly with any questions about your tax forms.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "a rental contract is created at 2.00/gpu/hr with a rental end date of march 31.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "on demand rentals are the highest priority and if met will stop interruptibles.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "when a client deletes a volume the space is automatically freed on the machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "all three require a host api key. regular client keys will receive a 401 error.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "gpu overview - current supply/demand counts pricing and stats for each gpu type",
    "s": "market-metrics.mdx"
  },
  {
    "t": "set disk pricing closer to your amortized cost. storage is not your bottleneck.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "a pending invoice has been generated but has not yet entered the payment phase.",
    "s": "payment.mdx"
  },
  {
    "t": "your cpu must support avx instruction set not all lower end cpus support this .",
    "s": "verification-stages.mdx"
  },
  {
    "t": "a verified machine consistently delivers server services to platform standards.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "use this message to identify and investigate the issue in your logs or metrics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "amdiommu on or inteliommu on depending on whether you have an amd or intel cpu.",
    "s": "vms.mdx"
  },
  {
    "t": "warning: vms interface much more directly with hardware than docker containers.",
    "s": "vms.mdx"
  },
  {
    "t": "confirm whether you qualify for a tax form based on your earnings and location",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "if you have raised the pricing you cannot extend the current rental contracts.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "as a host plan to offer 100% uptime for your machine during the rental period.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a rental contract is created at 2.50/gpu/hr with a rental end date of june 30.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if you set min gpus to 1 then clients can make instances with 1 2 4 or 8 gpus.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this is the fastest way to also see all the offers listed for a given machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "it reduces churn without requiring you to commit to a longer maximum duration.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "verification is one of the most common filters customers apply when searching.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "hosts may customize the information that appears on invoices by navigating to:",
    "s": "payment.mdx"
  },
  {
    "t": "pending: vms are not disabled but will try to enable once the machine is idle.",
    "s": "vms.mdx"
  },
  {
    "t": "important: vast.ai does not automatically withhold taxes. international hosts",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "states: unverified to verified to potentially deverified to unverified to ...",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the system hasn t yet completed enough testing to confirm platform standards.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "this is not a judgment of quality-only that no platform guarantee exists yet.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the template performance chart displays the earnings history from templates.",
    "s": "earning.mdx"
  },
  {
    "t": "clients require open ports to directly connect to the machine for most jobs.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "a short test workload will be executed to assess actual runtime performance.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "however you are locked into your pricing terms for the full contract length.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "data center hosts: do not set a duration longer than you can reliably honor.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "balanced scaling matters cpu/ram/pcie/bandwidth commensurate with gpu tier .",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "to qualify a machine must pass minimum baseline and health/stability checks.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "do verify gpu pcie connections provide full bandwidth and are not throttled.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "in order to apply you will need to first gather the required documentation:",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "this page in the console allows you to manage your earnings from referrals.",
    "s": "earning.mdx"
  },
  {
    "t": "vast.ai is based in california and does not currently collect or remit vat.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "changing the price does not change the rate on any existing rental contract",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "extending the offer end date allows new clients to rent for a longer period",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you list a 4a100 machine at 2.00/gpu/hr with an offer end date of march 31.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "location data is cached for up to 2 hours since it changes less frequently.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "the optimum sits somewhere in the middle and shifts with supply and demand.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the min bid price is a floor for the bidding system not an on-demand price.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "ensure you have the latest nvidia drivers installed at the time of listing.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "then for each machine id you will need to find the available instance ids.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "during the self-test the following components and conditions are verified:",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "your floor price should not be close to your expected actual rental price.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "settings alone won t help if your machines aren t reliable and up to date.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "there are no restrictions limitations or compliance holds on your account.",
    "s": "payment.mdx"
  },
  {
    "t": "there are no account limitations restrictions compliance reviews or holds.",
    "s": "payment.mdx"
  },
  {
    "t": "alternatively check out gpu market prices or the host earnings calculator.",
    "s": "payment.mdx"
  },
  {
    "t": "eliminate pcie thermal and power bottlenecks to maintain sustained clocks.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "what it means: a previously verified machine no longer meets requirements.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "once you accept your account will then be converted to a hosting account.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "by listing your machine you create an offer visible to potential clients.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "these workloads are transient. use short-term instances for this segment.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "researchers and developers testing models before committing to long runs.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "verify gpu pcie connections provide full bandwidth and are not throttled.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "the final verification outcome still depends on the factors listed below.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "ensure drivers/cuda and networking are correctly installed and reachable.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "hardware/system errors e.g. failing storage insufficient pcie bandwidth .",
    "s": "verification-stages.mdx"
  },
  {
    "t": "avoid downgrading hardware capacity e.g. reducing gpu count disk or ram .",
    "s": "verification-stages.mdx"
  },
  {
    "t": "program analysis for cuda-performance optimization e.g. via nvidia nsight",
    "s": "vms.mdx"
  },
  {
    "t": "your account can now list machines that are running the daemon software.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "hover over the rental button to see the discount rates that are offered.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "understanding this helps you target the right segment for your hardware:",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "this allows rentals to automatically continue beyond their initial term.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "cpu: favor strong server-grade cpus actual measured performance matters.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "do offer in-demand gpu models with adequate vram and balanced resources.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "vastai metrics gpu-trends rtx 4090 --full all data points vs sampled 20",
    "s": "market-metrics.mdx"
  },
  {
    "t": "over-committing especially data centers price lock-in on long contracts",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "gpu issues e.g. nvidia-smi/nvml failures container device init errors .",
    "s": "verification-stages.mdx"
  },
  {
    "t": "you will require a cpu and a chipset that support intel vt-d or amd-vi.",
    "s": "vms.mdx"
  },
  {
    "t": "make sure to read the section on iommu if you have an amd epyc system.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "cli via vastai metrics subcommands requires pip install vastai v1.0.4+",
    "s": "market-metrics.mdx"
  },
  {
    "t": "vastai metrics gpu-locations --gpu rtx 4090 h100sxm specific gpu types",
    "s": "market-metrics.mdx"
  },
  {
    "t": "test your machines before listing and after any configuration changes.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "any required identity tax or business verification has been completed.",
    "s": "payment.mdx"
  },
  {
    "t": "you must have a valid payout method connected to your vast.ai account.",
    "s": "payment.mdx"
  },
  {
    "t": "when issues arise fix them promptly-the automation will update status.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "a red error indicator will appear on your machine in the machines tab.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vms interface much more directly with hardware than docker containers.",
    "s": "vms.mdx"
  },
  {
    "t": "here you can generate and download invoices for your earning payouts.",
    "s": "earning.mdx"
  },
  {
    "t": "planning maintenance so that no active rental contracts are disrupted",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "in addition to gpu offers hosts can create volume offers on machines.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if the test fails: the cli will display detailed reasons for failure.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "week 2 friday: payment is submitted to your selected payout provider.",
    "s": "payment.mdx"
  },
  {
    "t": "offer in-demand gpu models with adequate vram and balanced resources.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "favor dc/workstation gpus ensure pcie lanes match cpu/ram to gpu tier",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "maintain compatible drivers/cuda and dependable symmetric networking.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "open /etc/default/grub and add to the grubcmdlinelinux the following:",
    "s": "vms.mdx"
  },
  {
    "t": "ensure your tax information is up to date with your payment provider",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "market conditions change over time so earnings cannot be guaranteed.",
    "s": "payment.mdx"
  },
  {
    "t": "> note: higher reliability greatly improves verification likelihood.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "do investigate red error indicators quickly review logs and metrics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "stripe connect stripe manages tax form delivery via stripe express.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the pricing you set is the rate you ll be paid for that commitment.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the ui shows june 30 as the latest rental end date on this machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the preferred method of testing your own machine is to run the cli.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "gpu locations - geographic distribution of gpus across the platform",
    "s": "market-metrics.mdx"
  },
  {
    "t": "why does my invoice show paid when i haven t received the funds yet",
    "s": "payment.mdx"
  },
  {
    "t": "enabling vm support significantly improves verification likelihood.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "downgrading hardware capacity e.g. reducing gpu count disk or ram .",
    "s": "verification-stages.mdx"
  },
  {
    "t": "pip install --upgrade vastai current snapshot - vastai metrics gpu",
    "s": "market-metrics.mdx"
  },
  {
    "t": "different customer types have very different duration preferences.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "use market data and your competitors pricing as a reference point.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the min gpu setting controls the smallest gpu partition you offer.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "if either requirement is not met an invoice will not be generated.",
    "s": "payment.mdx"
  },
  {
    "t": "government issued ids such as a passport for the business owner s",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "once you have the requiremed documentation to apply please visit:",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "you can find more information about vast s referral program here.",
    "s": "earning.mdx"
  },
  {
    "t": "if you are using vast.ai as a client do not use the same account.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "on february 1 client b rents the other 2 gpus from the new offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "when clicking on the set pricing button there is a min gpu field.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "this has the benefit of showing you the entire client experience.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "see full reference. historical trends - vastai metrics gpu-trends",
    "s": "market-metrics.mdx"
  },
  {
    "t": "your account can receive business payments for services provided.",
    "s": "payment.mdx"
  },
  {
    "t": "run jobs only through the jobs tab or the create job cli command.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "investigate red error indicators quickly review logs and metrics.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "what it means: newly added machines or machines under evaluation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "there is a link in the first paragraph to the hosting agreement.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "setting a gpu offer end date will update volume offer end dates.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "before running the test make sure: your machine has been listed.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "see full reference. location data - vastai metrics gpu-locations",
    "s": "market-metrics.mdx"
  },
  {
    "t": "lower prices fill your machines faster but each hour earns less.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "it typically takes up to two weeks to receive your first payout.",
    "s": "payment.mdx"
  },
  {
    "t": "your payout provider is not requesting additional documentation.",
    "s": "payment.mdx"
  },
  {
    "t": "ensure required ports are open and accessible a static ip helps.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "common causes network instability closed ports or low bandwidth.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "if you qualify for a form stripe will issue it directly to you.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the show machine command will show all your connected machines.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "for example if market rates rise you can t adjust mid-contract.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "your account balance must meet the 20 minimum payout threshold.",
    "s": "payment.mdx"
  },
  {
    "t": "avoid niche/mismatched configurations with low renter interest.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "most error messages are cleared within 1-2 hours of resolution.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "do pass the self-test maintain steady uptime during evaluation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "a contract or invoice from the datacenter linking the business",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "in the payout account section you can set up a payout account.",
    "s": "earning.mdx"
  },
  {
    "t": "vast.ai currently supports payouts through: wise paypal stripe",
    "s": "payment.mdx"
  },
  {
    "t": "do monitor health uptime thermals power and respond to alerts.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "configuring vms on your machine checking vm enablement status.",
    "s": "vms.mdx"
  },
  {
    "t": "one of the following third party certificates must be active:",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the business must be registered and up to date on all filings",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "vast does not offer support for getting your machine working.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the on-demand price is the price per hour for the gpu rental.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "maintain strong reliability to remain attractive once listed.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "install latest stable compatible versions use create job only",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "sustained 99.99% up to 99.9999%+ uptime is typically favored.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "keep the environment clean schedule work via create job only.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "volume offers will be unlisted when the machine is unlisted.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai set api-key 123123123123123 step 2: run the self-test",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "returns current supply demand and pricing for all gpu types.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "setting it like an on-demand price leaving gpus idle instead",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "proactively monitor hardware health and perform maintenance.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "proactive monitoring steady power/thermals minimize restarts",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "fix pcie/thermal bottlenecks maintain clocks correct drivers",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "scale up add gpus/ram avoid reductions that cause deverified",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "avoid misconfigurations that suppress benchmark performance.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "you can view your payout history for a selected date range.",
    "s": "earning.mdx"
  },
  {
    "t": "volume offer end dates must align with gpu offer end dates.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "if the test says the machine is not found or not rentable :",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "if the test passes you ll see: test completed successfully.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "all machines at 1x fragmentation or all at 8x missed demand",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "choose popular gpus/vram balance specs maintain reliability",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "avoid pairing high-end gpus with under-provisioned cpu/ram.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "monitor health uptime thermals power and respond to alerts.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "allowing thermal power or bandwidth instability under load.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "a previously verified machine no longer meets requirements.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "system continuous monitoring detects sustained degradation.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "avoid ignoring warnings or allowing instability to persist.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "managing your offers including pricing and offer end dates",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "for full details see the hosting agreement. offer end date",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "defaults to rtx 5090 4090 and 3090 over the last 24 hours.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "each endpoint allows up to 5 requests per second per user.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "i see my invoice is marked as pending. what does this mean",
    "s": "payment.mdx"
  },
  {
    "t": "other billing details you would like displayed on invoices",
    "s": "payment.mdx"
  },
  {
    "t": "important: vast.ai does not automatically withhold taxes.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the reserved discount pricing is determined by the hosts.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "common issues to check: make sure to test the networking.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai self-test machine 12345 step 3: review the results",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "vastai metrics gpu-locations --rented false only unrented",
    "s": "market-metrics.mdx"
  },
  {
    "t": "customers often prefer very long durations or no maximum.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "review your utilization patterns and adjust periodically.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "your balance has reached the 20 minimum payout threshold.",
    "s": "payment.mdx"
  },
  {
    "t": "vast.ai only supports payouts through: wise paypal stripe",
    "s": "payment.mdx"
  },
  {
    "t": "niche/mismatched configurations with low renter interest.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "network high-speed symmetric stable bandwidth is favored.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "keep systems stable well-cooled and correctly configured.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "at least 1x pcie for every 2.5 tflops of gpu performance.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "container launch failures or repeated runtime exceptions.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "validate thermal/power headroom and bandwidth under load.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "example: multiple rental contracts from different offers",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "follow the official setup guide to install the vast cli:",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "three views are available at cloud.vast.ai/host/market/:",
    "s": "market-metrics.mdx"
  },
  {
    "t": "vastai metrics gpu-trends rtx 4090 h100sxm multiple gpus",
    "s": "market-metrics.mdx"
  },
  {
    "t": "this is one of the most commonly misconfigured settings.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "keep network connectivity stable avoid jitter and drops.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "common questions how can i have earnings as a vast user",
    "s": "earning.mdx"
  },
  {
    "t": "vastai list machine -v -z -g .5 -e 12/23/2027 -r 0 -m 1",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "once your account is created open the host setup guide.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the offer accepts new rentals until the offer end date.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "returns time-series data for supply demand and pricing.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "unrelated background workloads that consume gpu/cpu/io.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "keep drivers/cuda on compatible latest stable versions.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "some hosts may also need to add the following settings:",
    "s": "vms.mdx"
  },
  {
    "t": "direct discord or slack channel to vast.ai for support",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "the company must sign the datacenter hosting agreement",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "it s a great way to track how your outreach is growing",
    "s": "earning.mdx"
  },
  {
    "t": "clients have high expectations coming from aws or gcp.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "these values are determined by the individual host s .",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "there are two supported ways to test your own machine.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "then you can start an ubuntu terminal and run the cli.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "replace 12345 with your actual machine id in question.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you can also query the data directly via the rest api.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "duration controls how long a rental contract can last.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "upgrade links verify routing/ports monitor jitter/loss",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "proper vm support is very sensitive to hardware setup.",
    "s": "vms.mdx"
  },
  {
    "t": "overall machine reliability under simulated workloads",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "a payout method is connected to your vast.ai account.",
    "s": "payment.mdx"
  },
  {
    "t": "keep systems clean run workloads via create job only.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "pairing high-end gpus with under-provisioned cpu/ram.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "letting hidden background services consume resources.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "ignoring warnings or allowing instability to persist.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "> note: high-end gpus are more likely to be verified.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "either you disabled vms or our previous tests failed.",
    "s": "vms.mdx"
  },
  {
    "t": "the mingpu param controlling slicing explained below",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "space is listed in gigabytes and price in /gb/month.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "yes but changes only affect future rental contracts.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "existing rental contracts keep their original terms:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "you must keep the machine available until this date.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "1.2 authenticate your cli with your vast.ai account:",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "vastai metrics gpu --verified true --datacenter true",
    "s": "market-metrics.mdx"
  },
  {
    "t": "vastai metrics gpu-trends rtx 4090 --raw json output",
    "s": "market-metrics.mdx"
  },
  {
    "t": "breaking a contract early carries a serious penalty.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "overheating undervolting or unstable power delivery.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "keep the latest drivers/cuda aligned with workloads.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "prefer nvme monitor smart ensure sustained bandwidth",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "do maintain consistent uptime with minimal downtime.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "fast reliable internet: at least 10mbps per machine.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "at least 1 physical cpu core 2 hyperthreads per gpu.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "re-check health after changes to confirm resolution.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "vat is not currently specified on vast.ai invoices.",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "the hardware can not be used for any other purposes",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "./vastai search offers machineid 12345 verified any",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "client a s contract stays at 2.00 through march 31.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "they can additionally be unlisted with the command:",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "friday: invoice is generated and marked as pending.",
    "s": "payment.mdx"
  },
  {
    "t": "--- frequently asked questions when will i get paid",
    "s": "payment.mdx"
  },
  {
    "t": "confirm required ports and end-to-end reachability.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "avoid unnecessary reboots or configuration changes.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "windows graphics e.g. for rendering or cloud gaming",
    "s": "vms.mdx"
  },
  {
    "t": "for further reference refer to preparing the iommu.",
    "s": "vms.mdx"
  },
  {
    "t": "on most machines this should be enabled by default.",
    "s": "vms.mdx"
  },
  {
    "t": "client b s contract stays at 2.50 through june 30.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "the cli will display detailed reasons for failure.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "try un-listing your machine then listing it again.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "host earnings depend on several factors including:",
    "s": "payment.mdx"
  },
  {
    "t": "network instability closed ports or low bandwidth.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "reducing hardware below the created specification.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "check that virtualization is enabled in your bios.",
    "s": "vms.mdx"
  },
  {
    "t": "vastai unlist volume out of sync rental contracts",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "there are no active clients currently renting it.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "what s the right fragmentation vs. demand balance",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "every setting in this guide affects that balance.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "your payout account is active and fully verified.",
    "s": "payment.mdx"
  },
  {
    "t": "maintain consistent uptime with minimal downtime.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "high-speed symmetric stable bandwidth is favored.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "all gpus on the machine must be of the same type.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "seconds between data points e.g. 3600 for hourly",
    "s": "market-metrics.mdx"
  },
  {
    "t": "pricing in a vacuum without checking competitors",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "manage thermals and power to prevent throttling.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "step-by-step guide step 0: install the vast cli",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "market metrics data is updated every 5 minutes.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "set disk pricing closer to your amortized cost.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "other due dilligence documentation as required",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "there are three ways to access market metrics:",
    "s": "market-metrics.mdx"
  },
  {
    "t": "vastai metrics gpu-locations --raw json output",
    "s": "market-metrics.mdx"
  },
  {
    "t": "think of your listing as a product on a shelf.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "set disk pricing higher than you might expect.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "vram: more vram improves performance profiles.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "the min bid price for interruptible instances",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "use the filters in the ui to select reserved.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "apply the suggested fixes and rerun the test.",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "historical trends - vastai metrics gpu-trends",
    "s": "market-metrics.mdx"
  },
  {
    "t": "vastai metrics gpu-trends rtx 4090 single gpu",
    "s": "market-metrics.mdx"
  },
  {
    "t": "regular client keys will receive a 401 error.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "are you over- or under-provisioned on storage",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "when your machines are idle you earn nothing.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "before selecting a payout method verify that:",
    "s": "payment.mdx"
  },
  {
    "t": "avoid frequent restarts or unplanned outages.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "fast ssd storage with at least 128gb per gpu.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "at least 3 open ports per gpu 100 recommended",
    "s": "verification-stages.mdx"
  },
  {
    "t": "--- minimum guidelines for listing on vast.ai",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the owner must undergo identity verification",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "hosts sell gpu resources on the marketplace.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "together these form the terms of your offer.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "on january 20 you decide to raise the price.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "1.1 get your api key: api keys documentation",
    "s": "how-to-self-test.mdx"
  },
  {
    "t": "location data - vastai metrics gpu-locations",
    "s": "market-metrics.mdx"
  },
  {
    "t": "this depends entirely on your network setup.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "--- payout schedule minimum payout threshold",
    "s": "payment.mdx"
  },
  {
    "t": "for full details see the hosting agreement.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "vastai metrics gpu-trends all all gpu types",
    "s": "market-metrics.mdx"
  },
  {
    "t": "current snapshot - verified datacenter gpus",
    "s": "market-metrics.mdx"
  },
  {
    "t": "your account can receive business payments.",
    "s": "payment.mdx"
  },
  {
    "t": "hardware gpu: type memory and count matter.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "you must create a new account for hosting.",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "rest api endpoints see api reference below",
    "s": "market-metrics.mdx"
  },
  {
    "t": "use short-term instances for this segment.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "to view and download invoices navigate to:",
    "s": "payment.mdx"
  },
  {
    "t": "do use the latest compatible drivers/cuda.",
    "s": "understanding-verification.mdx"
  },
  {
    "t": "an open port range mapped to each machine.",
    "s": "verification-stages.mdx"
  },
  {
    "t": "cuda version greater than or equal to 12.0",
    "s": "verification-stages.mdx"
  },
  {
    "t": "the equipment must be owned by a business",
    "s": "datacenter-status.mdx"
  },
  {
    "t": "it includes both paid and unpaid amounts.",
    "s": "earning.mdx"
  },
  {
    "t": "historical trends - rtx 4090 hourly steps",
    "s": "market-metrics.mdx"
  },
  {
    "t": "pass your host api key as a bearer token.",
    "s": "market-metrics.mdx"
  },
  {
    "t": "--- quick reference: settings at a glance",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "the service is available in your country.",
    "s": "payment.mdx"
  },
  {
    "t": "invoices are generated weekly on fridays.",
    "s": "payment.mdx"
  },
  {
    "t": "minimum guidelines for listing on vast.ai",
    "s": "verification-stages.mdx"
  },
  {
    "t": "common questions does vast.ai handle vat",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "what rate balances occupancy and revenue",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "what s your absolute floor cost of power",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "from the payout history section you can:",
    "s": "payment.mdx"
  },
  {
    "t": "configuring your machine to support vms.",
    "s": "vms.mdx"
  },
  {
    "t": "how the offer becomes a rental contract",
    "s": "hosting-overview.mdx"
  },
  {
    "t": "how can i have earnings as a vast user",
    "s": "earning.mdx"
  },
  {
    "t": "file your taxes accurately and on time",
    "s": "guide-to-taxes.mdx"
  },
  {
    "t": "are drivers current at time of listing",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "only commit to what you can guarantee.",
    "s": "optimization-guide.mdx"
  },
  {
    "t": "my account is not generating invoices.",
    "s": "payment.mdx"
  },
  {
    "t": "how much can i make hosting on vast.ai",
    "s": "payment.mdx"
  },
  {
    "t": "i see my invoice is marked as pending.",
    "s": "payment.mdx"
  },
  {
    "t": "off: vms are disabled on your machine.",
    "s": "vms.mdx"
  }
];
  const OLD_DOC_ASSETS = [
  {
    "src": "/images/console-earning.webp",
    "s": "earning.mdx"
  },
  {
    "src": "/images/console-earning-2.webp",
    "s": "earning.mdx"
  },
  {
    "src": "/images/console-earning-3.webp",
    "s": "earning.mdx"
  },
  {
    "src": "/images/console-earning-4.webp",
    "s": "earning.mdx"
  },
  {
    "src": "/images/offer-contract-lifecycle.png",
    "s": "hosting-overview.mdx"
  },
  {
    "src": "/images/hosting-overview.webp",
    "s": "hosting-overview.mdx"
  },
  {
    "src": "/images/hosting-overview-2.webp",
    "s": "hosting-overview.mdx"
  }
];
  const MOVED_OLD_DOC_GUIDANCE = [
  {
    "path": "/host/account-hosting-agreement",
    "t": "Use this page when a host account, hosting agreement, or Machines tab is not behaving as expected.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/account-hosting-agreement",
    "t": "Yes. Use a dedicated account for hosting. Do not use the same account for both client rentals and host operations, because that setup is unsupported and can cause account and machine-management issues.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/account-hosting-agreement",
    "t": "Once your host account is created, open the host setup guide. There is a link in the first paragraph to the hosting agreement. Read through the agreement. Once you accept, your account is converted to a hosting account, and a Machines link appears in the navigation.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/account-hosting-agreement",
    "t": "Your account must be enabled for hosting and the hosting agreement must be accepted. After the account is converted to a host account, the Machines navigation and other host features should become available.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Prepare the host machine before installing the Vast host software, including OS, BIOS, driver, power, thermal, and stability checks.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Before installing, make sure the host has supported same-type GPUs, native Ubuntu/Linux, an AVX-capable CPU, at least one physical CPU core per listed GPU, adequate RAM, fast SSD/NVMe storage, compatible GPU drivers, stable public networking, and enough direct ports.",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "For verification, the self-test preflight enforces the current minimum thresholds (CUDA support, reliability gate, direct ports, PCIe bandwidth, internet bandwidth, VRAM, system RAM).",
    "s": "how-to-self-test.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Current listing guidance requires Ubuntu 24.04 LTS. Confirm it works with your GPU driver, Docker, storage setup, and the Vast host installer before listing a production host.",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Use a stable NVIDIA driver that supports your GPU and a CUDA runtime compatible with the Vast self-test image family.",
    "s": "understanding-verification.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Enable virtualization and IOMMU in BIOS if you plan to support VMs; check IOMMU guidance especially on AMD EPYC systems.",
    "s": "vms.mdx"
  },
  {
    "path": "/host/hardware-prep",
    "t": "Disable unattended kernel and driver updates; plan updates through Maintenance Windows instead.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/installing-host-software",
    "t": "Install the Vast host software from the official setup flow, then verify that the daemon, Docker, storage, and GPU runtime are healthy.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/installing-host-software",
    "t": "Copy the current install command from the official Vast host setup page after your account is host-enabled.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/storage-setup",
    "t": "Use fast SSD/NVMe storage mounted predictably for Docker and Vast workloads. Current listing guidance expects at least 128 GB of fast SSD storage per GPU.",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/storage-setup",
    "t": "Space allocated to rented volume offers is subtracted from the storage available to GPU offers.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/network-ports",
    "t": "Configure public networking, direct ports, firewalls, and router forwarding before verification.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/network-ports",
    "t": "The self-test requires at least 3 direct ports per listed GPU.",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/supported-hardware",
    "t": "Use this page before buying hardware, installing the host software, or listing a machine.",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/supported-hardware",
    "t": "Passing the minimum requirements makes a machine eligible for verification. It does not guarantee verification, search placement, rentals, or earnings.",
    "s": "how-to-self-test.mdx"
  },
  {
    "path": "/host/supported-hardware",
    "t": "These are baseline expectations for listing a machine:",
    "s": "verification-stages.mdx"
  },
  {
    "path": "/host/supported-hardware",
    "t": "Do not size the rest of the machine as an afterthought. A high-end GPU host with weak CPU, low RAM, poor PCIe layout, slow storage, or unstable networking is less likely to pass verification or deliver good renter experience.",
    "s": "understanding-verification.mdx"
  },
  {
    "path": "/host/supported-hardware",
    "t": "VM support is optional, but it can affect search visibility and demand for some renters. VM support depends on CPU, chipset, BIOS, IOMMU, kernel, and GPU behavior.",
    "s": "vms.mdx"
  },
  {
    "path": "/host/maintenance-windows",
    "t": "Wait until active rental contracts have ended or there are no running instances before planned maintenance. Unlisting prevents new rental contracts, but it does not end existing contracts.",
    "s": "hosting-overview.mdx"
  },
  {
    "path": "/host/reliability-uptime",
    "t": "Reliability can drop when the platform observes instability, failed starts, disconnections, downtime, network failures, driver or GPU failures, thermal or power events, or active rental disruption.",
    "s": "understanding-verification.mdx"
  },
  {
    "path": "/host/reliability-uptime",
    "t": "Reliability greater than 0.90 is a self-test preflight gate.",
    "s": "how-to-self-test.mdx"
  }
];
  const PAGE_PARENT_SOURCES = {
    "/host/account-hosting-agreement": ["hosting-overview.mdx"],
    "/host/common-errors-diagnostics": ["how-to-self-test.mdx", "verification-stages.mdx", "vms.mdx"],
    "/host/common-host-questions": ["hosting-overview.mdx", "how-to-self-test.mdx", "verification-stages.mdx", "payment.mdx", "optimization-guide.mdx"],
    "/host/community": ["hosting-overview.mdx"],
    "/host/first-24-hours": ["hosting-overview.mdx", "how-to-self-test.mdx"],
    "/host/fleet-operations": ["hosting-overview.mdx", "optimization-guide.mdx", "market-metrics.mdx"],
    "/host/glossary": ["hosting-overview.mdx", "how-to-self-test.mdx", "optimization-guide.mdx", "verification-stages.mdx", "understanding-verification.mdx"],
    "/host/hardware-prep": ["hosting-overview.mdx", "verification-stages.mdx", "understanding-verification.mdx", "how-to-self-test.mdx", "vms.mdx"],
    "/host/headless-install": ["hosting-overview.mdx", "how-to-self-test.mdx", "vms.mdx"],
    "/host/hosting-agreement": ["hosting-overview.mdx"],
    "/host/installing-host-software": ["hosting-overview.mdx"],
    "/host/maintenance-windows": ["hosting-overview.mdx"],
    "/host/network-ports": ["hosting-overview.mdx", "how-to-self-test.mdx", "verification-stages.mdx"],
    "/host/not-in-search": ["hosting-overview.mdx", "verification-stages.mdx", "optimization-guide.mdx"],
    "/host/persona-decision-guide": ["hosting-overview.mdx", "understanding-verification.mdx", "verification-stages.mdx"],
    "/host/pricing-your-listing": ["optimization-guide.mdx", "hosting-overview.mdx"],
    "/host/quickstart": ["hosting-overview.mdx", "how-to-self-test.mdx"],
    "/host/reliability-uptime": ["understanding-verification.mdx", "verification-stages.mdx", "how-to-self-test.mdx"],
    "/host/removing-recreating-machines": ["hosting-overview.mdx", "verification-stages.mdx"],
    "/host/self-test-reference": ["how-to-self-test.mdx"],
    "/host/storage-setup": ["verification-stages.mdx", "hosting-overview.mdx"],
    "/host/supported-hardware": ["verification-stages.mdx", "understanding-verification.mdx", "how-to-self-test.mdx", "vms.mdx"],
    "/host/workload-policy": ["hosting-overview.mdx"]
  };
  const STATE_KEY = 'vast-old-docs-highlight-enabled';
  let active = false;
  let lastPath = '';
  let observer = null;

  function normalize(text) {
    return String(text || '')
      .toLowerCase()
      .replace(/[\u2018\u2019\u201A\u201B]/g, "'")
      .replace(/[\u201C\u201D\u201E\u201F]/g, '"')
      .replace(/[\u2013\u2014]/g, '-')
      .replace(/https?:\/\/\S+/g, ' ')
      .replace(/\$+/g, '')
      .replace(/[^a-z0-9./:+_<>%$ -]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function hostLikePath() {
    return location.pathname === '/host/docs-change-review' || location.pathname.startsWith('/host/');
  }

  function normalizeAssetPath(value) {
    if (!value) return '';
    const raw = String(value).trim();
    try {
      const url = new URL(raw, location.origin);
      const proxied = url.searchParams.get('url');
      if (proxied && url.pathname.includes('/_next/image')) {
        return normalizeAssetPath(proxied);
      }
      return decodeURIComponent(url.pathname).replace(/\/+$/, '');
    } catch {
      return raw.split(/[?#]/)[0].replace(/\/+$/, '');
    }
  }

  function assetPathsFromSrcset(srcset) {
    return String(srcset || '')
      .split(',')
      .map((part) => normalizeAssetPath(part.trim().split(/\s+/)[0]))
      .filter(Boolean);
  }

  function ensureStyle() {
    if (document.getElementById('vast-old-docs-highlight-style')) return;
    const style = document.createElement('style');
    style.id = 'vast-old-docs-highlight-style';
    style.textContent = `
      .vast-old-docs-toggle {
        position: fixed;
        right: 18px;
        bottom: 88px;
        z-index: 2147483000;
        display: none;
        align-items: center;
        gap: 8px;
        border: 1px solid rgba(245, 158, 11, 0.75);
        border-radius: 999px;
        padding: 8px 12px;
        background: rgba(24, 24, 27, 0.94);
        color: #fff7ed;
        font: 600 12px/1.1 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
        cursor: pointer;
      }
      .vast-old-docs-toggle[data-visible="true"] { display: inline-flex; }
      .vast-old-docs-toggle[data-active="true"] { background: #7c2d12; color: #fff7ed; }
      .vast-old-docs-toggle-count {
        display: inline-flex;
        min-width: 20px;
        height: 20px;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.16);
        font-size: 11px;
      }
      .vast-old-docs-reused {
        outline: 1px solid rgba(245, 158, 11, 0.75) !important;
        background: rgba(245, 158, 11, 0.20) !important;
        box-shadow: inset 0 -0.55em rgba(245, 158, 11, 0.20) !important;
        border-radius: 4px;
      }
      .vast-old-docs-reused:hover {
        outline-color: rgba(251, 191, 36, 1) !important;
      }
      .vast-old-docs-reused::selection { background: rgba(245, 158, 11, 0.45); }
      .vast-old-docs-reused-media {
        position: relative;
        outline: 3px solid rgba(14, 165, 233, 0.9) !important;
        outline-offset: 3px;
        background: rgba(14, 165, 233, 0.10) !important;
        border-radius: 6px;
      }
      .vast-old-docs-reused-media img,
      img.vast-old-docs-reused-media {
        outline: 3px solid rgba(14, 165, 233, 0.9) !important;
        outline-offset: 3px;
        border-radius: 6px;
      }
      .vast-old-docs-reused-media::after {
        content: attr(data-vast-old-doc-kind);
        position: absolute;
        top: 8px;
        left: 8px;
        z-index: 3;
        padding: 4px 7px;
        border-radius: 999px;
        background: rgba(2, 132, 199, 0.94);
        color: #f0f9ff;
        font: 700 11px/1 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: 0;
        pointer-events: none;
      }
      .vast-old-docs-parent-badge {
        display: inline-flex;
        align-items: center;
        max-width: 100%;
        margin: 0 0 1rem 0;
        padding: 0.45rem 0.65rem;
        border: 1px solid rgba(14, 165, 233, 0.55);
        border-radius: 6px;
        background: rgba(14, 165, 233, 0.10);
        color: #075985;
        font: 600 12px/1.35 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: 0;
        overflow-wrap: anywhere;
      }
      .dark .vast-old-docs-parent-badge {
        color: #bae6fd;
        background: rgba(14, 165, 233, 0.18);
        border-color: rgba(125, 211, 252, 0.50);
      }
    `;
    document.head.appendChild(style);
  }

  function ensureButton() {
    ensureStyle();
    let btn = document.getElementById('vast-old-docs-highlight-toggle');
    if (btn) return btn;
    btn = document.createElement('button');
    btn.id = 'vast-old-docs-highlight-toggle';
    btn.className = 'vast-old-docs-toggle';
    btn.type = 'button';
    btn.title = 'Demo helper: highlight content reused from the old host docs, including text blocks and images. Remove old-docs-highlight-demo.js before PR.';
    btn.innerHTML = '<span class="vast-old-docs-toggle-label">Old content</span><span class="vast-old-docs-toggle-count">0</span>';
    btn.addEventListener('click', () => {
      active = !active;
      localStorage.setItem(STATE_KEY, active ? '1' : '0');
      applyHighlights();
    });
    document.body.appendChild(btn);
    return btn;
  }

  function contentRoot() {
    return document.querySelector('[data-page-href]') ||
      document.querySelector('main article') ||
      document.querySelector('main [data-page-content]') ||
      document.querySelector('main') ||
      document.body;
  }

  function candidateElements() {
    const root = contentRoot();
    return Array.from(root.querySelectorAll('p, [data-as="p"], li, td, th, h1, h2, h3, h4, blockquote, code, pre'))
      .filter((el) => {
        if (el.closest('#vast-old-docs-highlight-toggle')) return false;
        if (el.closest('nav, header, footer, aside, button')) return false;
        const text = normalize(el.textContent);
        return text.length >= 38;
      });
  }

  function mediaElements() {
    const root = contentRoot();
    return Array.from(root.querySelectorAll('img, source, video, object, embed'))
      .filter((el) => {
        if (el.closest('#vast-old-docs-highlight-toggle')) return false;
        if (el.closest('nav, header, footer, aside, button')) return false;
        return true;
      });
  }

  function mediaPaths(el) {
    const paths = [
      el.currentSrc,
      el.getAttribute('src'),
      el.getAttribute('data-src'),
      el.getAttribute('poster'),
      el.getAttribute('data-poster')
    ].map(normalizeAssetPath).filter(Boolean);

    paths.push(...assetPathsFromSrcset(el.getAttribute('srcset')));
    return Array.from(new Set(paths));
  }

  function findAssetMatch(el) {
    const paths = mediaPaths(el);
    for (const path of paths) {
      for (const asset of OLD_DOC_ASSETS) {
        const oldPath = normalizeAssetPath(asset.src);
        if (path === oldPath || path.endsWith(oldPath)) return asset;
      }
    }
    return null;
  }

  function mediaHighlightTarget(el) {
    const linked = el.closest('a');
    if (linked && linked.querySelectorAll('img, source, video, object, embed').length === 1) return linked;
    const picture = el.closest('picture');
    if (picture) return picture;
    const figure = el.closest('figure');
    if (figure) return figure;
    const parent = el.parentElement;
    if (parent && ['P', 'DIV'].includes(parent.tagName) && parent.querySelectorAll('img, source, video, object, embed').length === 1) {
      return parent;
    }
    return el;
  }

  function findMatch(text) {
    if (!text) return null;
    for (const phrase of OLD_DOC_PHRASES) {
      if (text.includes(phrase.t)) return phrase;
      if (text.length >= 50 && phrase.t.length >= 70 && phrase.t.includes(text)) return phrase;
    }
    return null;
  }

  function findMovedGuidanceMatch(text) {
    if (!text) return null;
    for (const item of MOVED_OLD_DOC_GUIDANCE) {
      if (item.path && item.path !== location.pathname) continue;
      const movedText = normalize(item.t);
      if (text.includes(movedText)) {
        return {
          s: item.s,
          moved: true
        };
      }
    }
    return null;
  }

  function currentParentSources() {
    return PAGE_PARENT_SOURCES[location.pathname] || [];
  }

  function clearHighlights() {
    document.querySelectorAll('.vast-old-docs-parent-badge').forEach((el) => el.remove());
    document.querySelectorAll('.vast-old-docs-reused, .vast-old-docs-reused-media').forEach((el) => {
      el.classList.remove('vast-old-docs-reused');
      el.classList.remove('vast-old-docs-reused-media');
      el.removeAttribute('data-vast-old-doc-source');
      el.removeAttribute('data-vast-old-doc-kind');
      if (el.getAttribute('title') === el.dataset.vastOldTitle) el.removeAttribute('title');
      delete el.dataset.vastOldTitle;
    });
  }

  function markOldContent(el, className, source, title, kind) {
    el.classList.add(className);
    el.dataset.vastOldDocSource = source;
    el.dataset.vastOldTitle = title;
    if (kind) el.dataset.vastOldDocKind = kind;
    el.title = el.dataset.vastOldTitle;
  }

  function addParentBadge() {
    const sources = currentParentSources();
    if (!sources.length) return;
    const root = contentRoot();
    const badge = document.createElement('div');
    badge.className = 'vast-old-docs-parent-badge';
    badge.textContent = 'Old parent docs: ' + sources.join(', ');

    const persona = root.querySelector(':scope > .persona-chips');
    if (persona && persona.nextSibling) {
      persona.parentNode.insertBefore(badge, persona.nextSibling);
    } else if (persona) {
      persona.parentNode.appendChild(badge);
    } else {
      root.insertBefore(badge, root.firstChild);
    }
  }

  function applyHighlights() {
    const btn = ensureButton();
    btn.dataset.visible = hostLikePath() ? 'true' : 'false';
    btn.dataset.active = active ? 'true' : 'false';
    const label = btn.querySelector('.vast-old-docs-toggle-label');
    const count = btn.querySelector('.vast-old-docs-toggle-count');
    clearHighlights();

    let matches = 0;
    const highlighted = new Set();
    if (active && hostLikePath()) {
      addParentBadge();
      for (const el of candidateElements()) {
        const normalizedText = normalize(el.textContent);
        const match = findMatch(normalizedText) || findMovedGuidanceMatch(normalizedText);
        if (!match) continue;
        if (!highlighted.has(el)) {
          matches += 1;
          highlighted.add(el);
        }
        const title = match.moved
          ? 'Old docs moved/reworked guidance from ' + match.s
          : 'Old docs reused text from ' + match.s;
        markOldContent(el, 'vast-old-docs-reused', match.s, title);
      }
      for (const el of mediaElements()) {
        const match = findAssetMatch(el);
        if (!match) continue;
        const target = mediaHighlightTarget(el);
        if (!highlighted.has(target)) {
          matches += 1;
          highlighted.add(target);
        }
        markOldContent(target, 'vast-old-docs-reused-media', match.s, 'Old docs reused image from ' + match.s, 'old image');
      }
    }

    label.textContent = active ? 'Old content on' : 'Old content off';
    count.textContent = String(matches);
  }

  function scheduleApply() {
    window.clearTimeout(window.__vastOldDocsHighlightTimer);
    window.__vastOldDocsHighlightTimer = window.setTimeout(applyHighlights, 180);
  }

  function boot() {
    active = localStorage.getItem(STATE_KEY) === '1';
    ensureButton();
    applyHighlights();
    observer = new MutationObserver(scheduleApply);
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('popstate', scheduleApply);
    document.addEventListener('click', () => {
      window.setTimeout(() => {
        if (location.pathname !== lastPath) {
          lastPath = location.pathname;
          scheduleApply();
        }
      }, 250);
    }, true);
    window.setInterval(() => {
      if (location.pathname !== lastPath) {
        lastPath = location.pathname;
        scheduleApply();
      }
    }, 700);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
