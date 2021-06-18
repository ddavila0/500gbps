delete:
	- kubectl delete -k ./
create:
	- sed -i '/all.manager/c\all.manager\ $(shell kubectl get pods -l k8s-app=xrootd-redi-gc -o jsonpath="{.items[0].status.podIP}"):1213' xrootd-third-party-copy.cfg
	- kubectl apply -k ./
