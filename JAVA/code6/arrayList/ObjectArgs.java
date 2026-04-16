package arrayList;

public class ObjectArgs
{

	public static void main(String[] args)
	{
		Integer ia1=10;
		Integer ia2=20;
		changeIntegerArray(100,ia1,ia2);
		System.out.println(ia1+"\n"+ia2);
		
		Integer[] integerArr = {10,20,30,40,50};
		changeIntegerArray(100,integerArr);
		for(Integer i:integerArr)
			System.out.println(i);

	}
	
	public static void changeIntegerArray(int x,Integer...n)
	{
		for(int i=0;i<n.length;++i)
			n[i]*=x;
			
	}

}
