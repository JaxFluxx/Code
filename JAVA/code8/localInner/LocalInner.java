package localInner;

public class LocalInner
{

	public static void main(String[] args)
	{
//		LocalInner local=new LocalInner();
		class Pair
		{
			private int x;
			private int y;
			public Pair(int x, int y)
			{
				this.x=x;
				this.y=y;
			}
			public void show()
			{
				System.out.println("x="+ x +",y="+y);
			}
		}
		Pair pr=new Pair(100,200);
		pr.show();
	}
}
